from rest_framework import serializers

from games.models import PlayerAchievement
from games.serializers import PlayerAchievementSerializer
from .models import Badge, Friend, Player


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["steamid", "persona_name", "profile_url", "avatar_url", "avatar_full_url", "country_code", "time_created", "last_synced"]


class FriendSerializer(serializers.ModelSerializer):
    friend = PlayerSerializer(read_only=True)
    unlocked_achievements = serializers.SerializerMethodField()

    class Meta:
        model = Friend
        fields = ["friend", "friends_since", "unlocked_achievements"]

    def get_unlocked_achievements(self, obj):
        return PlayerAchievement.objects.filter(player=obj.friend, achieved=True).count()


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["badge_id", "level", "xp", "completion_time"]


class FriendAchievementSummarySerializer(serializers.Serializer):
    friend = PlayerSerializer()
    steam_appid = serializers.IntegerField()
    game_name = serializers.CharField()
    unlocked = serializers.IntegerField()
    total = serializers.IntegerField()
    achievements = PlayerAchievementSerializer(many=True)
