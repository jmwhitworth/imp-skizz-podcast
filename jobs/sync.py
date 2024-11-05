# Load django within this script when ran directly: https://stackoverflow.com/a/31444231
import sys, os, django
sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "podcast_index.settings")
django.setup()

import html, json, time
from podcasts.models import Podcast
from clients.YouTube import YouTube
from clients.Spotify import Spotify
from datetime import datetime, timedelta
from helpers import log


def syncYouTube(allPages:bool = False) -> None:
    """
        Uses the YouTube client to query the recent uploads from ImpAndSkizzPodcast.
        The results are then parsed and stored in the database if they don't exist.
    """
    SERVICE = "SYNC | YOUTUBE"
    
    maxResults = 5
    if allPages:
        maxResults = 50
    
    try:
        yt = YouTube()
        response = yt.recentUploads(maxResults=maxResults)
    except AttributeError as e:
        log(e, SERVICE, 'ERROR')
        return
    
    videos = response['items']
    
    # While the nextPageToken exists, keep using it to query the next page and assemble full list of videos
    if allPages:
        while 'nextPageToken' in response:
            newResponse = yt.recentUploads(maxResults=maxResults, pageToken=response['nextPageToken'])
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


def syncSpotify(allPages:bool = False) -> None:
    """
        Uses the Spotify client to query the recent shows from ImpAndSkizzPodcast.
        The results are then parsed and, if the show exists in the database, the Spotify URL is attached.
    """
    SERVICE = "SYNC | SPOTIFY"
    
    CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
    CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
    SHOW_ID = os.environ.get("SPOTIFY_SHOW_ID", "")
    
    client = Spotify(CLIENT_ID, CLIENT_SECRET)
    
    if allPages:
        episodes = client.allEpisodes(SHOW_ID)
    else:
        episodes = client.episodes(SHOW_ID)['items']
    
    for episode in episodes:
        if episode is not None:
            dt = datetime.strptime(episode['release_date'], "%Y-%m-%d")
            start_date = dt - timedelta(days=1)
            end_date = dt + timedelta(days=1)
            
            try:
                thisPodcast = Podcast.objects.filter(
                    release_date__range=(start_date, end_date)
                ).first()
                thisPodcast.spotify_url = f"https://open.spotify.com/episode/{episode['id']}"
                thisPodcast.preview_url = episode['audio_preview_url']
                thisPodcast.duration = episode['duration_ms']
                thisPodcast.save()
                log(f"Updated {thisPodcast.episode_number}'s Spotify URL", SERVICE)
            except (Podcast.DoesNotExist, AttributeError):
                log(f"Unable to find podcast with release_date of {str(dt)}", SERVICE, "ERROR")
                pass


if __name__ == "__main__":
    syncYouTube()
    syncSpotify()
