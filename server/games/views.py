from django.db.models import Count, Q
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Profile
from players.services import SteamAPIError
from .models import Game, NewsItem, PlayerAchievement, UserGame
from .serializers import NewsItemSerializer, PlayerAchievementSerializer, UserGameSerializer
from .services import sync_all_player_achievements, sync_game_achievements, sync_news_for_player, sync_player_friends, sync_player_library


class SyncSteamDataView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.player:
            return Response({"detail": "No Steam player is linked to this account."}, status=400)
        try:
            result = sync_player_library(profile.player)
            result.update(sync_player_friends(profile.player))
        except SteamAPIError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        profile.last_synced = result["last_synced"]
        profile.save(update_fields=["last_synced"])
        return Response(result)


class MyGamesView(ListAPIView):
    serializer_class = UserGameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = UserGame.objects.select_related("game").prefetch_related("game__genres", "game__categories")
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        if not profile.player:
            return qs.none()
        qs = qs.filter(player=profile.player)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(game__name__icontains=search)
        ordering = self.request.query_params.get("ordering", "-playtime_forever_minutes")
        allowed = {"playtime_forever_minutes", "-playtime_forever_minutes", "last_played_at", "-last_played_at", "game__name", "-game__name"}
        return qs.order_by(ordering if ordering in allowed else "-playtime_forever_minutes")


class MyGameDetailView(RetrieveAPIView):
    serializer_class = UserGameSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "game__steam_appid"
    lookup_url_kwarg = "steam_appid"

    def get_queryset(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        if not profile.player:
            return UserGame.objects.none()
        return UserGame.objects.select_related("game").prefetch_related("game__genres", "game__categories").filter(player=profile.player)


class MyAchievementsView(ListAPIView):
    serializer_class = PlayerAchievementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        if not profile.player:
            return PlayerAchievement.objects.none()
        return PlayerAchievement.objects.select_related("achievement", "achievement__game").filter(player=profile.player, achievement__game__steam_appid=self.kwargs["steam_appid"])

    def post(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.player:
            return Response({"detail": "No Steam player is linked to this account."}, status=400)
        try:
            result = sync_game_achievements(profile.player, kwargs["steam_appid"])
        except Game.DoesNotExist:
            return Response({"detail": "Game is not in this user's library."}, status=404)
        except SteamAPIError as exc:
            return Response({"detail": str(exc)}, status=502)
        return Response(result)


class MyNewsView(ListAPIView):
    serializer_class = NewsItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        if not profile.player:
            return NewsItem.objects.none()
        qs = NewsItem.objects.select_related("game").filter(game__owners__player=profile.player).distinct()
        appid = self.request.query_params.get("appid")
        if appid:
            qs = qs.filter(game__steam_appid=appid)
        return qs[:100]

    def post(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.player:
            return Response({"detail": "No Steam player is linked to this account."}, status=400)
        try:
            return Response(sync_news_for_player(profile.player))
        except SteamAPIError as exc:
            return Response({"detail": str(exc)}, status=502)


class AllMyAchievementsView(ListAPIView):
    serializer_class = PlayerAchievementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        if not profile.player:
            return PlayerAchievement.objects.none()
        qs = PlayerAchievement.objects.select_related("achievement", "achievement__game").filter(player=profile.player)
        status_filter = self.request.query_params.get("status")
        if status_filter == "unlocked":
            qs = qs.filter(achieved=True)
        elif status_filter == "locked":
            qs = qs.filter(achieved=False)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(achievement__display_name__icontains=search) | Q(achievement__game__name__icontains=search))
        ordering = self.request.query_params.get("ordering", "-unlocked_at")
        allowed = {"-unlocked_at", "unlocked_at", "achievement__display_name", "-achievement__global_percent", "achievement__global_percent"}
        return qs.order_by(ordering if ordering in allowed else "-unlocked_at", "achievement__display_name")


class AchievementSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.player:
            return Response({"total": 0, "unlocked": 0, "locked": 0, "completion_percent": 0, "games": []})
        qs = PlayerAchievement.objects.filter(player=profile.player)
        total = qs.count()
        unlocked = qs.filter(achieved=True).count()
        games = list(
            qs.values("achievement__game__steam_appid", "achievement__game__name", "achievement__game__header_image")
            .annotate(total=Count("id"), unlocked=Count("id", filter=Q(achieved=True)))
            .order_by("-unlocked", "achievement__game__name")
        )
        for game in games:
            game["completion_percent"] = round((game["unlocked"] / game["total"] * 100), 1) if game["total"] else 0
        return Response({
            "total": total,
            "unlocked": unlocked,
            "locked": total - unlocked,
            "completion_percent": round((unlocked / total * 100), 1) if total else 0,
            "games": games,
        })


class SyncAllAchievementsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.player:
            return Response({"detail": "No Steam player is linked to this account."}, status=400)
        try:
            max_games = int(request.query_params.get("max_games", 50))
            return Response(sync_all_player_achievements(profile.player, max_games=max_games))
        except (TypeError, ValueError):
            return Response({"detail": "max_games must be an integer."}, status=400)
        except SteamAPIError as exc:
            return Response({"detail": str(exc)}, status=502)
