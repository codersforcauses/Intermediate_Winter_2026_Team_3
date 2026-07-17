from django.urls import path
from .views import FriendAchievementsView, FriendGamesView, FriendProfileView, MyFriendsView

urlpatterns = [
    path("friends/", MyFriendsView.as_view(), name="my-friends"),
    path("friends/<str:steamid>/profile/", FriendProfileView.as_view(), name="friend-profile"),
    path("friends/<str:steamid>/games/", FriendGamesView.as_view(), name="friend-games"),
    path("friends/<str:steamid>/games/<int:steam_appid>/achievements/", FriendAchievementsView.as_view(), name="friend-achievements"),
]
