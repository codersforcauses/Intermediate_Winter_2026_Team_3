from rest_framework import serializers

from .models import Badge, Friend, Player


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            "steamid",
            "persona_name",
            "profile_url",
            "avatar_url",
            "avatar_full_url",
            "country_code",
            "time_created",
            "last_synced",
        ]


class FriendSerializer(serializers.ModelSerializer):
    friend = PlayerSerializer(read_only=True)

    class Meta:
        model = Friend
        fields = ["friend", "friends_since"]


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["badge_id", "level", "xp", "completion_time"]
