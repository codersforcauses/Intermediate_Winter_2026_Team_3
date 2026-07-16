from django.urls import path
from .views import MyFriendsView

urlpatterns = [path("friends/", MyFriendsView.as_view(), name="my-friends")]
