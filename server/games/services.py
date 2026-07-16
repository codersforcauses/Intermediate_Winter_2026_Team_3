from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from players.models import Friend, Player
from players.services import SteamAPIClient, SteamAPIError, unix_timestamp
from .models import Achievement, Game, PlayerAchievement, PlaytimeSnapshot, UserGame


def _icon_url(appid: int, icon_hash: str) -> str:
    if not icon_hash:
        return ""
    return f"https://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{icon_hash}.jpg"


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
    recent_by_appid = {
        item.get("appid"): item for item in client.get_recent_games(player.steamid)
    }

    touched_user_game_ids: list[int] = []
    for item in owned_games:
        appid = item.get("appid")
        if not appid:
            continue

        game, _ = Game.objects.update_or_create(
            steam_appid=appid,
            defaults={
                "name": item.get("name") or f"Steam App {appid}",
                "icon_url": _icon_url(appid, item.get("img_icon_url", "")),
                "header_image": _header_url(appid),
                "last_synced": now,
            },
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
                "last_played_at": unix_timestamp(item.get("rtime_last_played")),
                "last_synced": now,
            },
        )
        touched_user_game_ids.append(user_game.id)

        latest = user_game.snapshots.order_by("-recorded_at").first()
        if latest is None or latest.playtime_minutes != user_game.playtime_forever_minutes:
            PlaytimeSnapshot.objects.create(
                user_game=user_game,
                playtime_minutes=user_game.playtime_forever_minutes,
            )

    player.last_synced = now
    player.save()

    return {
        "games_synced": len(touched_user_game_ids),
        "last_synced": now,
    }


@transaction.atomic
def sync_player_friends(player: Player, client: SteamAPIClient | None = None) -> dict:
    client = client or SteamAPIClient()
    rows = client.get_friend_list(player.steamid)
    steamids = [str(row.get("steamid")) for row in rows if row.get("steamid")]

    summaries: dict[str, dict] = {}
    for start in range(0, len(steamids), 100):
        batch = steamids[start : start + 100]
        if not batch:
            continue
        payload = client._get(
            "ISteamUser/GetPlayerSummaries/v2/",
            {"steamids": ",".join(batch)},
        )
        summaries.update(
            {
                str(item.get("steamid")): item
                for item in payload.get("response", {}).get("players", [])
                if item.get("steamid")
            }
        )

    synced = 0
    for row in rows:
        friend_steamid = str(row.get("steamid", ""))
        if not friend_steamid or friend_steamid == player.steamid:
            continue
        summary = summaries.get(friend_steamid, {})
        friend_player, _ = Player.objects.update_or_create(
            steamid=friend_steamid,
            defaults={
                "persona_name": summary.get("personaname", ""),
                "profile_url": summary.get("profileurl", ""),
                "avatar_url": summary.get("avatar", ""),
                "avatar_full_url": summary.get("avatarfull", ""),
                "country_code": summary.get("loccountrycode", ""),
                "time_created": unix_timestamp(summary.get("timecreated")),
                "last_synced": timezone.now(),
            },
        )
        Friend.objects.update_or_create(
            player=player,
            friend=friend_player,
            defaults={"friends_since": unix_timestamp(row.get("friend_since"))},
        )
        synced += 1

    return {"friends_synced": synced}


@transaction.atomic
def sync_game_achievements(
    player: Player,
    appid: int,
    client: SteamAPIClient | None = None,
) -> dict:
    client = client or SteamAPIClient()
    game = Game.objects.get(steam_appid=appid)
    now = timezone.now()
    rows = client.get_player_achievements(player.steamid, appid)

    synced = 0
    for row in rows:
        api_name = row.get("apiname")
        if not api_name:
            continue
        achievement, _ = Achievement.objects.update_or_create(
            game=game,
            api_name=api_name,
            defaults={
                "display_name": row.get("name") or api_name,
                "description": row.get("description", ""),
            },
        )
        PlayerAchievement.objects.update_or_create(
            player=player,
            achievement=achievement,
            defaults={
                "achieved": bool(row.get("achieved")),
                "unlocked_at": unix_timestamp(row.get("unlocktime")),
                "last_synced": now,
            },
        )
        synced += 1

    return {"achievements_synced": synced}
