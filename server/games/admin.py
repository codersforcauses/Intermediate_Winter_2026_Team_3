from django.contrib import admin
from .models import (
    Achievement,
    Category,
    Game,
    Genre,
    NewsItem,
    PlayerAchievement,
    PlaytimeSnapshot,
    PriceHistory,
    Screenshot,
    UserGame,
)

admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Game)
admin.site.register(UserGame)
admin.site.register(PlaytimeSnapshot)
admin.site.register(PriceHistory)
admin.site.register(Screenshot)
admin.site.register(NewsItem)
admin.site.register(Achievement)
admin.site.register(PlayerAchievement)
