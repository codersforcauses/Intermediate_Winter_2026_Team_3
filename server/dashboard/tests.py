from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Profile
from games.models import Game, UserGame
from players.models import Player


class DashboardApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="dashboard-user", password="test-password")
        self.player = Player.objects.create(steamid="76561198000000000", persona_name="Test Player")
        Profile.objects.create(user=self.user, player=self.player)
        self.client.force_authenticate(user=self.user)

    def test_dashboard_returns_stored_stats(self):
        game = Game.objects.create(steam_appid=10, name="Test Game")
        UserGame.objects.create(player=self.player, game=game, playtime_forever_minutes=600)

        response = self.client.get("/api/dashboard/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["games_owned"], 1)
        self.assertEqual(payload["summary"]["total_playtime_hours"], 10.0)
        self.assertEqual(payload["top_games"][0]["game"]["name"], "Test Game")
