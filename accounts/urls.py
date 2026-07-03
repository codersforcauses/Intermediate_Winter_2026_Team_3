# accounts/urls.py
from django.urls import path
from .views import MyProfileView

urlpatterns = [
    path('profile/me/', MyProfileView.as_view(), name='my-profile'),
]