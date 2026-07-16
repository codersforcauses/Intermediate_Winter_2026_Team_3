from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Profile


class SessionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_anonymous_session(self):
        response = self.client.get("/api/auth/session/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"authenticated": False})

    def test_authenticated_session_creates_profile(self):
        user = User.objects.create_user(username="steam-user", password="test-password")
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/auth/session/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["authenticated"])
        self.assertTrue(Profile.objects.filter(user=user).exists())
