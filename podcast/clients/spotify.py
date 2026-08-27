from dataclasses import dataclass
from datetime import datetime

import requests
from django.conf import settings


@dataclass
class RemoteEpisode:
    episode_id: str
    release_date: datetime
    duration_ms: int
    href: str
    title: str
    description: str
    preview_url: str
    api_data: dict


class SpotifyClient:
    ENDPOINT_ACCOUNT: str = "https://accounts.spotify.com/api"
    ENDPOINT_API: str = "https://api.spotify.com/v1"

    def __init__(self):
        self.SHOW_ID = settings.SPOTIFY_SHOW_ID
        self.CLIENT_ID = settings.SPOTIFY_CLIENT_ID
        self.CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET
        self.BEARER_TOKEN = self._getBearerToken()

    def _getBearerToken(self) -> str:
        data = self._post(
            f"{self.ENDPOINT_ACCOUNT}/token",
            f"grant_type=client_credentials&client_id={self.CLIENT_ID}&client_secret={self.CLIENT_SECRET}",
        )
        if "access_token" not in data:
            raise RuntimeError(f"Spotify authentication failed: {data}")
        return data["access_token"]

    def _post(self, endpoint: str, data: str = "") -> dict:
        """Sends a POST request to the given Spotify API endpoint"""
        return requests.post(
            endpoint,
            headers={"Content-type": "application/x-www-form-urlencoded"},
            data=data,
        ).json()

    def _get(self, endpoint: str) -> dict:
        """Sends a GET request to the given Spotify API endpoint, uses BEARER token Auth"""
        return requests.get(
            endpoint, headers={"Authorization": f"Bearer {self.BEARER_TOKEN}"}
        ).json()

    def _fetch_episodes(self, limit: int = 5, offset: int = 0) -> dict:
        """Gets the recent episodes for the given Show"""
        return self._get(
            f"{self.ENDPOINT_API}/shows/{self.SHOW_ID}/episodes?limit={str(limit)}&offset={str(offset)}"
        )

    def fetch_all_episodes(self) -> list[RemoteEpisode]:
        """Gets all episodes for the given Show"""
        response = self._fetch_episodes(limit=50)
        episodes = response["items"]

        while response["next"] is not None:
            newResponse = self._get(response["next"])
            if "items" in newResponse:
                for item in newResponse["items"]:
                    episodes.append(item)
            response = newResponse

        return self._parse_episodes(episodes)

    def fetch_recent_episodes(self, limit: int = 50) -> list[RemoteEpisode]:
        """Gets the most recently released episodes for the given Show"""
        response = self._fetch_episodes(limit=limit)
        return self._parse_episodes(response.get("items", []))

    def _parse_episodes(self, items: list[dict]) -> list[RemoteEpisode]:
        return [
            RemoteEpisode(
                episode_id=item["id"],
                release_date=datetime.strptime(item["release_date"], "%Y-%m-%d"),
                duration_ms=item["duration_ms"],
                href=item.get("external_urls", {}).get("spotify", ""),
                preview_url=item.get("audio_preview_url", ""),
                title=item["name"],
                description=item.get("description", ""),
                api_data=item,
            )
            for item in items
        ]
