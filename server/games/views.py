from django.db.models import Count, Q, Sum
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from players.services import SteamAPIError
from accounts.models import Profile
from .models import Game, NewsItem, PlayerAchievement, UserGame
from .serializers import NewsItemSerializer, PlayerAchievementSerializer, UserGameSerializer
from .services import sync_game_achievements, sync_player_friends, sync_player_library


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
        return PlayerAchievement.objects.select_related("achievement", "achievement__game").filter(
            player=Profile.objects.get_or_create(user=self.request.user)[0].player,
            achievement__game__steam_appid=self.kwargs["steam_appid"],
        )

    def post(self, request, *args, **kwargs):
        try:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            if not profile.player:
                return Response({"detail": "No Steam player is linked to this account."}, status=400)
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
        return NewsItem.objects.select_related("game").filter(game__owners__player=profile.player).distinct()[:100]
