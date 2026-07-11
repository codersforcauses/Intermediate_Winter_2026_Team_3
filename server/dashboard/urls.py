from django.urls import path
from . import views

urlpatterns = [
    path('login-test/', views.login_test, name='login_test'),
]