from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from players.models import Friend, Player
from players.services import SteamAPIClient, unix_timestamp
from .models import Achievement, Game, NewsItem, PlayerAchievement, PlaytimeSnapshot, UserGame
from players.services import SteamAPIClient, SteamAPIError

def _icon_url(appid: int, icon_hash: str) -> str:
    return f"https://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{icon_hash}.jpg" if icon_hash else ""


def _header_url(appid: int) -> str:
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"


@transaction.atomic
def sync_player_library(player: Player, client: SteamAPIClient | None = None) -> dict:
    client = client or SteamAPIClient()
    now = timezone.now()
    summary = client.get_player_summary(player.steamid)
    if summary:
        player.persona_name = summary.get("personaname", player.persona_name)
        player.profile_url = summary.get("profileurl", player.profile_url)
        player.avatar_url = summary.get("avatar", player.avatar_url)
        player.avatar_full_url = summary.get("avatarfull", player.avatar_full_url)
        player.country_code = summary.get("loccountrycode", player.country_code)
        player.time_created = unix_timestamp(summary.get("timecreated")) or player.time_created

    owned_games = client.get_owned_games(player.steamid)
    recent_by_appid = {item.get("appid"): item for item in client.get_recent_games(player.steamid)}
    touched = []
    for item in owned_games:
        appid = item.get("appid")
        if not appid:
            continue
        game, _ = Game.objects.update_or_create(
            steam_appid=appid,
            defaults={"name": item.get("name") or f"Steam App {appid}", "icon_url": _icon_url(appid, item.get("img_icon_url", "")), "header_image": _header_url(appid), "last_synced": now},
        )
        recent = recent_by_appid.get(appid, {})
        user_game, _ = UserGame.objects.update_or_create(
            player=player,
            game=game,
            defaults={
                "playtime_forever_minutes": item.get("playtime_forever", 0) or 0,
                "playtime_recent_minutes": recent.get("playtime_2weeks", 0) or 0,
                "playtime_windows_minutes": item.get("playtime_windows_forever", 0) or 0,
                "playtime_mac_minutes": item.get("playtime_mac_forever", 0) or 0,
                "playtime_linux_minutes": item.get("playtime_linux_forever", 0) or 0,
                "last_played_at": unix_timestamp(item.get("rtime_last_played")), "last_synced": now,
            },
        )
        touched.append(user_game.id)
        latest = user_game.snapshots.order_by("-recorded_at").first()
        if latest is None or latest.playtime_minutes != user_game.playtime_forever_minutes:
            PlaytimeSnapshot.objects.create(user_game=user_game, playtime_minutes=user_game.playtime_forever_minutes)
    player.last_synced = now
    player.save()
    return {"games_synced": len(touched), "last_synced": now}


@transaction.atomic
def sync_player_friends(player: Player, client: SteamAPIClient | None = None) -> dict:
    client = client or SteamAPIClient()
    rows = client.get_friend_list(player.steamid)
    steamids = [str(row.get("steamid")) for row in rows if row.get("steamid")]
    summaries = {}
    for start in range(0, len(steamids), 100):
        summaries.update({str(item.get("steamid")): item for item in client.get_player_summaries(steamids[start:start + 100]) if item.get("steamid")})
    synced = 0
    for row in rows:
        sid = str(row.get("steamid", ""))
        if not sid or sid == player.steamid:
            continue
        summary = summaries.get(sid, {})
        friend_player, _ = Player.objects.update_or_create(
            steamid=sid,
            defaults={"persona_name": summary.get("personaname", ""), "profile_url": summary.get("profileurl", ""), "avatar_url": summary.get("avatar", ""), "avatar_full_url": summary.get("avatarfull", ""), "country_code": summary.get("loccountrycode", ""), "time_created": unix_timestamp(summary.get("timecreated")), "last_synced": timezone.now()},
        )
        Friend.objects.update_or_create(player=player, friend=friend_player, defaults={"friends_since": unix_timestamp(row.get("friend_since"))})
        synced += 1
    return {"friends_synced": synced}


@transaction.atomic
def sync_game_achievements(player: Player, appid: int, client: SteamAPIClient | None = None) -> dict:
    client = client or SteamAPIClient()
    game = Game.objects.get(steam_appid=appid)
    now = timezone.now()
    schema = {row.get("name"): row for row in client.get_game_schema(appid) if row.get("name")}
    global_rows = client.get_global_achievement_percentages(appid)
    global_percentages = {row.get("name"): row.get("percent") for row in global_rows if row.get("name")}
    rows = client.get_player_achievements(player.steamid, appid)
    synced = 0
    for row in rows:
        api_name = row.get("apiname")
        if not api_name:
            continue
        meta = schema.get(api_name, {})
        achievement, _ = Achievement.objects.update_or_create(
            game=game, api_name=api_name,
            defaults={"display_name": row.get("name") or meta.get("displayName") or api_name, "description": row.get("description") or meta.get("description", ""), "icon_url": meta.get("icon", ""), "locked_icon_url": meta.get("icongray", ""), "hidden": bool(meta.get("hidden", 0)), "global_percent": global_percentages.get(api_name)},
        )
        PlayerAchievement.objects.update_or_create(player=player, achievement=achievement, defaults={"achieved": bool(row.get("achieved")), "unlocked_at": unix_timestamp(row.get("unlocktime")), "last_synced": now})
        synced += 1
    return {"achievements_synced": synced, "steamid": player.steamid, "steam_appid": appid}


@transaction.atomic
def sync_news_for_player(player: Player, client: SteamAPIClient | None = None, game_limit: int = 15) -> dict:
    client = client or SteamAPIClient()
    now = timezone.now()
    games = Game.objects.filter(owners__player=player).order_by("-owners__playtime_forever_minutes")[:game_limit]
    synced = 0
    for game in games:
        for row in client.get_news_for_app(game.steam_appid):
            external_id = str(row.get("gid") or row.get("url") or "")
            if not external_id:
                continue
            NewsItem.objects.update_or_create(
                external_id=external_id,
                defaults={"game": game, "title": row.get("title") or "Steam news", "url": row.get("url") or f"https://store.steampowered.com/news/app/{game.steam_appid}", "author": row.get("author", ""), "published_at": unix_timestamp(row.get("date")) or now, "contents": row.get("contents", ""), "last_synced": now},
            )
            synced += 1
    return {"news_synced": synced, "games_checked": len(games)}


@transaction.atomic

def sync_all_player_achievements(

    player: Player,

    client: SteamAPIClient | None = None,

    max_games: int = 50,

) -> dict:

    client = client or SteamAPIClient()

    games = (

        UserGame.objects.filter(player=player)

        .select_related("game")

        .order_by("-playtime_forever_minutes")[:max(1, min(max_games, 100))]

    )

    games_checked = 0

    games_with_achievements = 0

    achievements_synced = 0

    games_failed = 0

    errors = []

    for user_game in games:

        games_checked += 1

        appid = user_game.game.steam_appid

        try:

            result = sync_game_achievements(

                player=player,

                appid=appid,

                client=client,

            )

        except SteamAPIError as exc:

            games_failed += 1

            error_message = f"{user_game.game.name} ({appid}): {exc}"

            errors.append(error_message)

            print(f"ACHIEVEMENT SYNC FAILED: {error_message}")

            continue

        count = result["achievements_synced"]

        achievements_synced += count

        if count > 0:

            games_with_achievements += 1

    return {

        "games_checked": games_checked,

        "games_with_achievements": games_with_achievements,

        "achievements_synced": achievements_synced,

        "games_failed": games_failed,

        "errors": errors[:10],

    }
