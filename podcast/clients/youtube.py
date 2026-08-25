import os
from dataclasses import dataclass
from datetime import datetime, timezone

import googleapiclient.discovery
from django.conf import settings


@dataclass
class RemoteVideo:
    id: str
    publishedAt: datetime
    title: str
    description: str
    api_data: dict


class YoutubeClient:
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = settings.YOUTUBE_API_KEY
    CHANNEL_ID = settings.YOUTUBE_CHANNEL_ID
    PLAYLIST_ID = "UU" + CHANNEL_ID[2:]

    def __init__(self):
        if not self.DEVELOPER_KEY:
            raise AttributeError("No YouTube API key provided")
        if not self.CHANNEL_ID:
            raise AttributeError("No YouTube channel ID provided")

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = str(
            int(settings.ENVIRONMENT == "local")
        )

        self.youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, developerKey=self.DEVELOPER_KEY
        )

    def _fetch_videos(self, max_results: int = 50, page_token: str = None) -> dict:
        if max_results < 1 or max_results > 50:
            raise ValueError("max_results must be between 1 and 50")

        request = self.youtube.playlistItems().list(
            part="snippet",
            playlistId=self.PLAYLIST_ID,
            maxResults=max_results,
            pageToken=page_token,
        )
        return request.execute()

    def fetch_all_uploads(self) -> list[RemoteVideo]:
        """Gets all uploads for the ImpAndSkizzPodcast channel."""
        videos = []
        page_token = None

        while True:
            response = self._fetch_videos(page_token=page_token)

            if not response or not response.get("items"):
                break

            videos.extend(
                [
                    RemoteVideo(
                        id=item["snippet"]["resourceId"]["videoId"],
                        publishedAt=datetime.strptime(
                            item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                        ).replace(tzinfo=timezone.utc),
                        title=item["snippet"]["title"],
                        description=item["snippet"]["description"],
                        api_data=item,
                    )
                    for item in response.get("items", [])
                ]
            )

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return videos

    def fetch_recent_uploads(self) -> list[RemoteVideo]:
        """Gets the recent uploads for the ImpAndSkizzPodcast channel."""
        response = self._fetch_videos()

        if not response or not response.get("items"):
            return []

        return [
            RemoteVideo(
                id=item["snippet"]["resourceId"]["videoId"],
                publishedAt=datetime.strptime(
                    item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                ).replace(tzinfo=timezone.utc),
                title=item["snippet"]["title"],
                description=item["snippet"]["description"],
                api_data=item,
            )
            for item in response.get("items", [])
        ]
