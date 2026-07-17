from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Profile
from games.models import Game, PlayerAchievement, UserGame
from games.serializers import PlayerAchievementSerializer
from games.services import sync_game_achievements
from players.services import SteamAPIClient, SteamAPIError, unix_timestamp
from .models import Friend
from .serializers import FriendSerializer, PlayerSerializer


class FriendMixin:
    def get_friend(self, request, steamid):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.player:
            return None
        relation = get_object_or_404(
            Friend.objects.select_related("friend"),
            player=profile.player,
            friend__steamid=steamid,
        )
        return relation.friend


class MyFriendsView(ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        if not profile.player:
            return Friend.objects.none()
        return Friend.objects.select_related("friend").filter(player=profile.player).order_by("friend__persona_name")


class FriendProfileView(FriendMixin, APIView):
    """Return a read-only profile for one of the signed-in user's Steam friends."""

    permission_classes = [IsAuthenticated]

    def get(self, request, steamid):
        friend = self.get_friend(request, steamid)
        profile, _ = Profile.objects.get_or_create(user=request.user)

        try:
            client = SteamAPIClient()
            summary = client.get_player_summary(friend.steamid) or {}
        except SteamAPIError as exc:
            return Response({"detail": str(exc)}, status=502)

        # Keep the local friend card fresh while retaining values Steam omitted.
        friend.persona_name = summary.get("personaname", friend.persona_name)
        friend.profile_url = summary.get("profileurl", friend.profile_url)
        friend.avatar_url = summary.get("avatarmedium", summary.get("avatar", friend.avatar_url))
        friend.avatar_full_url = summary.get("avatarfull", friend.avatar_full_url)
        friend.country_code = summary.get("loccountrycode", friend.country_code)
        friend.time_created = unix_timestamp(summary.get("timecreated")) or friend.time_created
        friend.last_synced = timezone.now()
        friend.save(update_fields=[
            "persona_name", "profile_url", "avatar_url", "avatar_full_url",
            "country_code", "time_created", "last_synced",
        ])

        games_private = False
        try:
            owned_payload = client.get_owned_games(friend.steamid)
            recent_payload = client.get_recent_games(friend.steamid)
        except SteamAPIError:
            owned_payload = []
            recent_payload = []
            games_private = True

        local_games = {
            game.steam_appid: game
            for game in Game.objects.filter(
                steam_appid__in=[row.get("appid") for row in owned_payload if row.get("appid")]
            )
        }
        my_appids = set()
        if profile.player:
            my_appids = set(
                UserGame.objects.filter(player=profile.player).values_list("game__steam_appid", flat=True)
            )

        def game_payload(row):
            appid = int(row.get("appid", 0))
            local = local_games.get(appid)
            icon_hash = row.get("img_icon_url", "")
            return {
                "steam_appid": appid,
                "name": row.get("name") or (local.name if local else f"App {appid}"),
                "header_image": local.header_image if local and local.header_image else f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg",
                "icon_url": (
                    local.icon_url if local and local.icon_url
                    else f"https://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{icon_hash}.jpg" if icon_hash
                    else ""
                ),
                "playtime_forever_minutes": int(row.get("playtime_forever", 0) or 0),
                "playtime_recent_minutes": int(row.get("playtime_2weeks", 0) or 0),
                "shared": appid in my_appids,
            }

        owned_games = sorted(
            (game_payload(row) for row in owned_payload),
            key=lambda row: row["playtime_forever_minutes"],
            reverse=True,
        )
        recent_games = sorted(
            (game_payload(row) for row in recent_payload),
            key=lambda row: row["playtime_recent_minutes"],
            reverse=True,
        )

        total_minutes = sum(row["playtime_forever_minutes"] for row in owned_games)
        unlocked = PlayerAchievement.objects.filter(player=friend, achieved=True).count()
        persona_state = int(summary.get("personastate", 0) or 0)
        state_names = {
            0: "Offline", 1: "Online", 2: "Busy", 3: "Away",
            4: "Snooze", 5: "Looking to trade", 6: "Looking to play",
        }

        return Response({
            "friend": PlayerSerializer(friend).data,
            "status": state_names.get(persona_state, "Unknown"),
            "real_name": summary.get("realname", ""),
            "current_game": summary.get("gameextrainfo", ""),
            "current_game_appid": int(summary.get("gameid", 0) or 0) or None,
            "last_logoff": unix_timestamp(summary.get("lastlogoff")),
            "games_private": games_private,
            "summary": {
                "games_owned": len(owned_games),
                "shared_games": sum(1 for row in owned_games if row["shared"]),
                "achievements_unlocked": unlocked,
                "total_playtime_minutes": total_minutes,
                "total_playtime_hours": round(total_minutes / 60, 1),
            },
            "recent_games": recent_games[:6],
            "top_games": owned_games[:12],
        })


class FriendGamesView(FriendMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, steamid):
        friend = self.get_friend(request, steamid)
        profile, _ = Profile.objects.get_or_create(user=request.user)
        games = UserGame.objects.select_related("game").filter(player=profile.player)
        payload = [{"steam_appid": row.game.steam_appid, "name": row.game.name, "header_image": row.game.header_image} for row in games]
        return Response({"friend": PlayerSerializer(friend).data, "games": payload})


class FriendAchievementsView(FriendMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, steamid, steam_appid):
        friend = self.get_friend(request, steamid)
        game = get_object_or_404(Game, steam_appid=steam_appid)
        rows = PlayerAchievement.objects.select_related("achievement", "achievement__game").filter(player=friend, achievement__game=game)
        return Response({
            "friend": PlayerSerializer(friend).data,
            "steam_appid": game.steam_appid,
            "game_name": game.name,
            "unlocked": rows.filter(achieved=True).count(),
            "total": rows.count(),
            "achievements": PlayerAchievementSerializer(rows, many=True).data,
        })

    def post(self, request, steamid, steam_appid):
        friend = self.get_friend(request, steamid)
        try:
            result = sync_game_achievements(friend, steam_appid)
        except Game.DoesNotExist:
            return Response({"detail": "This game is not available in the local library."}, status=404)
        except SteamAPIError as exc:
            return Response({"detail": f"Steam could not provide this friend's achievements. Their game details may be private. {exc}"}, status=502)
        return Response(result)
