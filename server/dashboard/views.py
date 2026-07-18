from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from games.models import PlayerAchievement, UserGame
from games.serializers import UserGameSerializer
from accounts.models import Profile


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        player = profile.player
        if not player:
            return Response({"detail": "No Steam player is linked to this account."}, status=400)

        games = UserGame.objects.select_related("game").prefetch_related("game__genres", "game__categories").filter(player=player)
        total_minutes = games.aggregate(total=Sum("playtime_forever_minutes"))["total"] or 0
        top_games = games.order_by("-playtime_forever_minutes")[:5]

        return Response({
            "profile": {
                "username": request.user.username,
                "steamid": player.steamid,
                "persona_name": player.persona_name,
                "avatar_url": player.avatar_full_url or player.avatar_url,
                "country_code": player.country_code,
                "last_synced": profile.last_synced,
            },
            "summary": {
                "friends": player.friends.count(),
                "games_owned": games.count(),
                "achievements_unlocked": PlayerAchievement.objects.filter(player=player, achieved=True).count(),
                "total_playtime_minutes": total_minutes,
                "total_playtime_hours": round(total_minutes / 60, 2),
            },
            "top_games": UserGameSerializer(top_games, many=True).data,
        })
