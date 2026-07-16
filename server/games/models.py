from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    steam_appid = models.PositiveIntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=255)
    short_description = models.TextField(blank=True)
    header_image = models.URLField(blank=True)
    icon_url = models.URLField(blank=True)
    developers = models.CharField(max_length=500, blank=True)
    publishers = models.CharField(max_length=500, blank=True)
    release_date = models.DateField(null=True, blank=True)
    is_free = models.BooleanField(default=False)

    review_score = models.PositiveSmallIntegerField(null=True, blank=True)
    review_score_desc = models.CharField(max_length=50, blank=True)
    total_reviews = models.PositiveIntegerField(null=True, blank=True)
    total_positive = models.PositiveIntegerField(null=True, blank=True)
    total_negative = models.PositiveIntegerField(null=True, blank=True)

    genres = models.ManyToManyField(Genre, blank=True, related_name="games")
    categories = models.ManyToManyField(Category, blank=True, related_name="games")
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserGame(models.Model):
    player = models.ForeignKey(
        "players.Player", on_delete=models.CASCADE, related_name="owned_games"
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="owners")
    playtime_forever_minutes = models.PositiveIntegerField(default=0)
    playtime_recent_minutes = models.PositiveIntegerField(default=0)
    playtime_windows_minutes = models.PositiveIntegerField(default=0)
    playtime_mac_minutes = models.PositiveIntegerField(default=0)
    playtime_linux_minutes = models.PositiveIntegerField(default=0)
    last_played_at = models.DateTimeField(null=True, blank=True)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "game"], name="unique_player_game"
            )
        ]
        indexes = [
            models.Index(fields=["player", "-playtime_forever_minutes"]),
            models.Index(fields=["player", "-last_played_at"]),
        ]
        ordering = ["-playtime_forever_minutes", "game__name"]

    @property
    def playtime_hours(self):
        return round(self.playtime_forever_minutes / 60, 2)

    def __str__(self):
        return f"{self.player} — {self.game}"


class PlaytimeSnapshot(models.Model):
    user_game = models.ForeignKey(
        UserGame, on_delete=models.CASCADE, related_name="snapshots"
    )
    playtime_minutes = models.PositiveIntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["recorded_at"]
        indexes = [models.Index(fields=["user_game", "recorded_at"])]

    def __str__(self):
        return f"{self.user_game}: {self.playtime_minutes} minutes"


class PriceHistory(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="price_history")
    price_amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.game.name} — {self.price_amount} {self.currency}"


class Screenshot(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="screenshots")
    url = models.URLField()

    def __str__(self):
        return f"Screenshot for {self.game.name}"


class NewsItem(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="news_items")
    external_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    title = models.CharField(max_length=500)
    url = models.URLField()
    author = models.CharField(max_length=255, blank=True)
    published_at = models.DateTimeField()
    contents = models.TextField(blank=True)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


class Achievement(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="achievements")
    api_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon_url = models.URLField(blank=True)
    locked_icon_url = models.URLField(blank=True)
    hidden = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "api_name"], name="unique_game_achievement"
            )
        ]

    def __str__(self):
        return f"{self.display_name} ({self.game.name})"


class PlayerAchievement(models.Model):
    player = models.ForeignKey(
        "players.Player", on_delete=models.CASCADE, related_name="achievement_progress"
    )
    achievement = models.ForeignKey(
        Achievement, on_delete=models.CASCADE, related_name="player_progress"
    )
    achieved = models.BooleanField(default=False)
    unlocked_at = models.DateTimeField(null=True, blank=True)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "achievement"],
                name="unique_player_achievement",
            )
        ]
        indexes = [models.Index(fields=["player", "achieved"])]

    def __str__(self):
        status = "unlocked" if self.achieved else "locked"
        return f"{self.player} — {self.achievement} ({status})"
