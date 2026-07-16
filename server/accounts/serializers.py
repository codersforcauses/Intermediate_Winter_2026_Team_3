from rest_framework import serializers

from players.serializers import PlayerSerializer
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "username",
            "player",
            "last_synced",
            "is_public_profile",
            "preferred_currency",
        ]
        read_only_fields = ["last_synced", "player"]
