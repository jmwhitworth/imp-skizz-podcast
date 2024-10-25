import sys, os, django, html

# Load django within this script when ran directly: https://stackoverflow.com/a/31444231
sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "podcast_index.settings")
django.setup()

from podcasts.models import Podcast
from datetime import datetime
import googleapiclient.discovery


class YouTube():
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.environ.get("YOUTUBE_API_KEY")
    CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID")
    
    def __init__(self, local:bool=True):
        if self.DEVELOPER_KEY == "":
            print("YouTube Client Error: No YouTube API key provided")
            return
        
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = str(int(os.environ.get("ENVIRONMENT", "production") == "local"))
        
        self.youtube = googleapiclient.discovery.build(
        self.api_service_name,
        self.api_version,
        developerKey = self.DEVELOPER_KEY
    )
    
    def recentUploads(self, pageToken:str=None) -> dict:
        """Gets the recent uploads for the ImpAndSkizzPodcast channel.
        
        Args:
            pageToken (str, optional): The 'nextPageToken' to use with pagination. Defaults to None.
        """
        if self.DEVELOPER_KEY == "":
            print("YouTube Client Error: No YouTube API key provided - Aborting recentUploads()")
            return {'items':[]}
        
        request = self.youtube.search().list(
            part='snippet',
            channelId=self.CHANNEL_ID,
            type='video',
            order='date',
            maxResults=50,
            pageToken=pageToken
        )
        return request.execute()


def queryAndSaveRecentVideos(allPages:bool = False) -> None:
    """
        Uses the YouTubeClient to query the recent uploads from ImpAndSkizzPodcast.
        The results are then parsed and stored in the database if they don't exist.
    """
    yt = YouTube()
    response = yt.recentUploads()
    videos = response['items']
    
    # While the nextPageToken exists, keep using it to query the next page and assemble full list of videos
    if allPages:
        while 'nextPageToken' in response:
            newResponse = yt.recentUploads(response['nextPageToken'])
            if 'items' in newResponse:
                for item in newResponse['items']:
                    videos.append(item)
            response = newResponse
    
    for video in videos:
        # Parse the video information for storing in the database
        raw_title = html.unescape(str(video['snippet']['title']))
        id = video['id']['videoId']
        dt = datetime.strptime(video['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
        
        try:
            title = raw_title.split('|')[0].strip()
            episode_number = int(raw_title.lower().split('(ep')[1].replace(')',''))
        except IndexError:
            continue
        
        print(f"YT: Querying podcast {str(episode_number)}: {title}")
        Podcast.objects.get_or_create(
            title = title,
            episode_number = episode_number,
            youtube_id = id,
            release_date = dt
        )

if __name__ == "__main__":
    queryAndSaveRecentVideos()
