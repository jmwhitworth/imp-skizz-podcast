import os
from datetime import datetime, timedelta

import googleapiclient.discovery


class YouTube:
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.environ.get("YOUTUBE_API_KEY", "")
    CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "")

    def __init__(self):
        if not bool(self.DEVELOPER_KEY):
            raise AttributeError("No YouTube API key provided")

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = str(
            int(os.environ.get("ENVIRONMENT", "production") == "local")
        )

        self.youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, developerKey=self.DEVELOPER_KEY
        )

    def recentUploads(self, maxResults: int = 5, pageToken: str = None) -> dict:
        """Gets the recent uploads for the ImpAndSkizzPodcast channel.

        Args:
            maxResults (int, optional): The number of results per query. Defaults to 5.
            pageToken (str, optional): The 'nextPageToken' to use with pagination. Defaults to None.
        """
        if self.CHANNEL_ID == "":
            raise AttributeError("No YouTube channel ID provided")

        last_month = datetime.now() - timedelta(days=30)

        request = self.youtube.search().list(
            part="snippet",
            channelId=self.CHANNEL_ID,
            type="video",
            order="date",
            maxResults=maxResults,
            publishedAfter=last_month.strftime("%Y-%m-%dT%H:%M:%SZ"),
            pageToken=pageToken,
        )
        return request.execute()
