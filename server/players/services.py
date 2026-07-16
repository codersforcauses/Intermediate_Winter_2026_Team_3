from __future__ import annotations

from datetime import datetime, timezone as dt_timezone
from typing import Any

import requests
from django.conf import settings


class SteamAPIError(RuntimeError):
    """Raised when Steam cannot provide a usable response."""


class SteamAPIClient:
    BASE_URL = "https://api.steampowered.com"

    def __init__(self, api_key: str | None = None, timeout: int = 15):
        self.api_key = api_key or settings.SOCIAL_AUTH_STEAM_API_KEY
        self.timeout = timeout
        if not self.api_key or self.api_key == "your-key-here":
            raise SteamAPIError("STEAM_API_KEY is not configured")

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        query = {"key": self.api_key, **(params or {})}
        try:
            response = requests.get(
                f"{self.BASE_URL}/{endpoint.lstrip('/')}",
                params=query,
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise SteamAPIError("Steam API request failed") from exc

        if not isinstance(payload, dict):
            raise SteamAPIError("Steam API returned an unexpected response")
        return payload

    def get_player_summary(self, steamid: str) -> dict[str, Any] | None:
        payload = self._get(
            "ISteamUser/GetPlayerSummaries/v2/",
            {"steamids": steamid},
        )
        players = payload.get("response", {}).get("players", [])
        return players[0] if players else None

    def get_owned_games(self, steamid: str) -> list[dict[str, Any]]:
        payload = self._get(
            "IPlayerService/GetOwnedGames/v1/",
            {
                "steamid": steamid,
                "include_appinfo": 1,
                "include_played_free_games": 1,
            },
        )
        return payload.get("response", {}).get("games", []) or []

    def get_recent_games(self, steamid: str) -> list[dict[str, Any]]:
        payload = self._get(
            "IPlayerService/GetRecentlyPlayedGames/v1/",
            {"steamid": steamid},
        )
        return payload.get("response", {}).get("games", []) or []

    def get_friend_list(self, steamid: str) -> list[dict[str, Any]]:
        payload = self._get(
            "ISteamUser/GetFriendList/v1/",
            {"steamid": steamid, "relationship": "friend"},
        )
        return payload.get("friendslist", {}).get("friends", []) or []

    def get_player_achievements(self, steamid: str, appid: int) -> list[dict[str, Any]]:
        payload = self._get(
            "ISteamUserStats/GetPlayerAchievements/v1/",
            {"steamid": steamid, "appid": appid, "l": "english"},
        )
        playerstats = payload.get("playerstats", {})
        if playerstats.get("success") is False:
            return []
        return playerstats.get("achievements", []) or []


def unix_timestamp(value: Any) -> datetime | None:
    try:
        timestamp = int(value)
    except (TypeError, ValueError):
        return None
    if timestamp <= 0:
        return None
    return datetime.fromtimestamp(timestamp, tz=dt_timezone.utc)
