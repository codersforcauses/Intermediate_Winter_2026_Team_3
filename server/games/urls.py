from django.urls import path
from .views import AchievementSummaryView, AllMyAchievementsView, MyAchievementsView, MyGameDetailView, MyGamesView, MyNewsView, SyncAllAchievementsView, SyncSteamDataView

urlpatterns = [
    path("sync/", SyncSteamDataView.as_view(), name="sync-steam"),
    path("games/", MyGamesView.as_view(), name="my-games"),
    path("games/<int:steam_appid>/", MyGameDetailView.as_view(), name="my-game-detail"),
    path("games/<int:steam_appid>/achievements/", MyAchievementsView.as_view(), name="my-achievements"),
    path("achievements/", AllMyAchievementsView.as_view(), name="all-my-achievements"),
    path("achievements/summary/", AchievementSummaryView.as_view(), name="achievement-summary"),
    path("achievements/sync/", SyncAllAchievementsView.as_view(), name="sync-all-achievements"),
    path("news/", MyNewsView.as_view(), name="my-news"),
]
