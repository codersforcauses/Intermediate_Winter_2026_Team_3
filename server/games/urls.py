from django.urls import path

from .views import MyAchievementsView, MyGameDetailView, MyGamesView, MyNewsView, SyncSteamDataView

urlpatterns = [
    path("sync/", SyncSteamDataView.as_view(), name="steam-sync"),
    path("games/", MyGamesView.as_view(), name="my-games"),
    path("games/<int:steam_appid>/", MyGameDetailView.as_view(), name="my-game-detail"),
    path("games/<int:steam_appid>/achievements/", MyAchievementsView.as_view(), name="my-achievements"),
    path("news/", MyNewsView.as_view(), name="my-news"),
]
