# Load django within this script when ran directly: https://stackoverflow.com/a/31444231
import sys, os, django
sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "podcast_index.settings")
django.setup()

import html
from podcasts.models import Podcast
from clients.YouTube import YouTube
from datetime import datetime
from helpers import log

SERVICE = "SYNC"


def queryAndSaveRecentVideos(allPages:bool = False) -> None:
    """
        Uses the YouTubeClient to query the recent uploads from ImpAndSkizzPodcast.
        The results are then parsed and stored in the database if they don't exist.
    """
    try:
        yt = YouTube()
        
        if not allPages:
            log(f"Fetching recent uploads...", SERVICE)
        else:
            log(f"Fetching all uploads...", SERVICE)

        response = yt.recentUploads()
    except ValueError as e:
        log(e, SERVICE, 'ERROR')
    
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
        
        log(f"Running Fetch/Create {str(episode_number)}: {title}", SERVICE)
        Podcast.objects.get_or_create(
            title = title,
            episode_number = episode_number,
            youtube_id = id,
            release_date = dt
        )
    
    log("Sync complete", SERVICE)


if __name__ == "__main__":
    queryAndSaveRecentVideos()
