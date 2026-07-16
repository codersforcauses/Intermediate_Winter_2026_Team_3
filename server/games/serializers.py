from rest_framework import serializers

from .models import Achievement, Game, NewsItem, PlayerAchievement, UserGame


class GameSerializer(serializers.ModelSerializer):
    genres = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    categories = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Game
        fields = [
            "steam_appid",
            "name",
            "short_description",
            "header_image",
            "icon_url",
            "developers",
            "publishers",
            "release_date",
            "is_free",
            "review_score",
            "review_score_desc",
            "total_reviews",
            "genres",
            "categories",
            "last_synced",
        ]


class UserGameSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)
    playtime_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = UserGame
        fields = [
            "game",
            "playtime_forever_minutes",
            "playtime_recent_minutes",
            "playtime_windows_minutes",
            "playtime_mac_minutes",
            "playtime_linux_minutes",
            "playtime_hours",
            "last_played_at",
            "last_synced",
        ]


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = [
            "api_name",
            "display_name",
            "description",
            "icon_url",
            "locked_icon_url",
            "hidden",
        ]


class PlayerAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = PlayerAchievement
        fields = ["achievement", "achieved", "unlocked_at", "last_synced"]


class NewsItemSerializer(serializers.ModelSerializer):
    game_name = serializers.CharField(source="game.name", read_only=True)
    steam_appid = serializers.IntegerField(source="game.steam_appid", read_only=True)

    class Meta:
        model = NewsItem
        fields = [
            "external_id",
            "steam_appid",
            "game_name",
            "title",
            "url",
            "author",
            "published_at",
            "contents",
        ]
