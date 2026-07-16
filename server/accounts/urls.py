from django.urls import path

from .views import CsrfTokenView, LogoutView, MyProfileView, SessionView

urlpatterns = [
    path("profile/me/", MyProfileView.as_view(), name="my-profile"),
    path("auth/session/", SessionView.as_view(), name="auth-session"),
    path("auth/csrf/", CsrfTokenView.as_view(), name="auth-csrf"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
]
