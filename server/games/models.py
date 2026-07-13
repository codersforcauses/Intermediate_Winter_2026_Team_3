from django.db import models

# Create your models here.
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
    developers = models.CharField(max_length=255, blank=True)
    publishers = models.CharField(max_length=255, blank=True)
    release_date = models.DateField(null=True, blank=True)
    is_free = models.BooleanField(default=False)

    # Aggregate review stats (from Steam Store API)
    review_score = models.PositiveSmallIntegerField(null=True, blank=True)  # e.g. 97 (percent positive)
    review_score_desc = models.CharField(max_length=50, blank=True)  # e.g. "Overwhelmingly Positive"
    total_reviews = models.PositiveIntegerField(null=True, blank=True)
    total_positive = models.PositiveIntegerField(null=True, blank=True)
    total_negative = models.PositiveIntegerField(null=True, blank=True)

    genres = models.ManyToManyField(Genre, blank=True, related_name='games')
    categories = models.ManyToManyField(Category, blank=True, related_name='games')

    last_synced = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class PriceHistory(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='price_history')
    price_amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.game.name} — {self.price_amount} {self.currency}"


class Screenshot(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='screenshots')
    url = models.URLField()

    def __str__(self):
        return f"Screenshot for {self.game.name}"


class NewsItem(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='news_items')
    title = models.CharField(max_length=255)
    url = models.URLField()
    published_at = models.DateTimeField()
    contents = models.TextField(blank=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class Achievement(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='achievements')
    api_name = models.CharField(max_length=255)  # Steam's internal key, e.g. "ACH_WIN_ONE_GAME"
    display_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon_url = models.URLField(blank=True)

    class Meta:
        unique_together = ('game', 'api_name')

    def __str__(self):
        return f"{self.display_name} ({self.game.name})"