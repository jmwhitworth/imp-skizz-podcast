from logging import getLogger
from typing import Optional

from django.db import transaction

from status.models import StatusModelMixin as Status

from .clients.llm import LLMClient
from .clients.spotify import SpotifyClient
from .clients.youtube import YoutubeClient
from .models import Podcast, SpotifyEpisode, YoutubeVideo

logger = getLogger(__name__)


def podcast_create_for_all_youtubevideos() -> int:
    """
    Creates podcast entries from YouTube videos that do not yet have associated podcasts.
    Returns the number of podcasts created.
    """
    videos = (
        YoutubeVideo.objects.filter(podcasts__isnull=True)
        .not_archived()
        .order_by("published_at")
    )

    if not videos.exists():
        return 0

    logger.info(f"Creating podcasts from {videos.count()} YouTube videos")

    created_count = 0
    for video in videos.iterator():
        podcast = podcast_create_from_youtubevideo(video)
        if podcast:
            created_count += 1

    logger.info(f"Created {created_count} podcasts from YouTube videos")
    return created_count


def podcast_create_from_youtubevideo(youtubevideo: YoutubeVideo) -> Optional[Podcast]:
    """
    Creates a podcast entry from a given YouTube video instance.
    Returns the created Podcast instance if successful, None otherwise.
    """
    data = LLMClient().identify_episode(youtubevideo.title)
    if data is None or data.season is None or data.episode is None:
        youtubevideo.status = Status.ARCHIVED
        youtubevideo.save(update_fields=["status"])
        logger.warning(
            f"Could not identify episode for video: {youtubevideo.video_id} - {youtubevideo.title}. Marked as archived."
        )
        return None

    podcast, created = Podcast.objects.get_or_create(
        season=data.season,
        episode=data.episode,
        defaults={
            "title": youtubevideo.title,
            "release_date": youtubevideo.published_at.date(),
            "youtube_video": youtubevideo,
            "status": Status.PUBLISHED,
        },
    )
    if not created:
        youtubevideo.status = Status.ARCHIVED
        youtubevideo.save(update_fields=["status"])
        logger.warning(
            f"Podcast already exists for video: {youtubevideo.video_id} - {youtubevideo.title}. Marked as archived."
        )

    return podcast


def podcast_create_from_youtubevideo_id(youtubevideo_id) -> Optional[Podcast]:
    """
    Creates a podcast entry from a given YouTube video ID.
    Returns the created Podcast instance if successful, None otherwise.
    """
    video = YoutubeVideo.objects.filter(id=youtubevideo_id).first()
    if not video:
        return None

    return podcast_create_from_youtubevideo(video)


def podcast_debrand_title(podcast_id) -> bool:
    """
    Updates the title of the given podcast to remove branding and episode identifiers.
    Returns True if the title was updated, False otherwise.
    """
    podcast = Podcast.objects.filter(id=podcast_id).first()
    if not podcast:
        return False

    new_title = LLMClient().rename_episode(podcast.title)

    if new_title != podcast.title:
        podcast.title = new_title
        podcast.full_clean()
        podcast.save(update_fields=["title"])
        return True
    return False


def youtubevideo_import() -> int:
    """
    Imports recent YouTube videos and creates corresponding podcast entries.
    Returns the number of YouTube videos imported and corresponding podcast entries created.
    """
    items = YoutubeClient().fetch_recent_uploads()

    if not items:
        return 0

    with transaction.atomic():
        records = YoutubeVideo.objects.bulk_create(
            [
                YoutubeVideo(
                    video_id=item.id,
                    published_at=item.publishedAt,
                    title=item.title,
                    description=item.description,
                    api_data=item.api_data,
                    status=Status.PUBLISHED,
                )
                for item in items
            ],
            update_conflicts=True,
            unique_fields=["video_id"],
            update_fields=["title", "description", "api_data"],
        )

    podcast_create_for_all_youtubevideos()

    return len(records)


def spotifyepisode_auto_assign_podcast(spotifyepisode_id) -> Optional[Podcast]:
    """
    Assigns a Spotify episode to a podcast entry.
    Returns the assigned Podcast instance if successful, None otherwise.
    """
    episode = SpotifyEpisode.objects.filter(id=spotifyepisode_id).first()
    if not episode:
        return None

    candidates = Podcast.objects.filter(release_date=episode.release_date)
    podcast = candidates.first() if candidates.count() == 1 else None

    if not podcast:
        return None

    podcast.spotify_episode = episode
    podcast.full_clean()
    podcast.save(update_fields=["spotify_episode"])

    return podcast


def spotifyepisode_import() -> int:
    """
    Imports recent Spotify episodes and creates corresponding podcast entries.
    Returns the number of Spotify episodes imported and corresponding podcast entries created.
    """
    items = SpotifyClient().fetch_recent_episodes()

    if not items:
        return 0

    with transaction.atomic():
        SpotifyEpisode.objects.bulk_create(
            [
                SpotifyEpisode(
                    episode_id=item.episode_id,
                    release_date=item.release_date,
                    duration_ms=item.duration_ms,
                    href=item.href,
                    preview_url=item.preview_url,
                    title=item.title,
                    description=item.description,
                    api_data=item.api_data,
                    status=Status.PUBLISHED,
                )
                for item in items
            ],
            update_conflicts=True,
            unique_fields=["episode_id"],
            update_fields=["title", "description", "api_data", "preview_url"],
        )

    # Re-fetch from db to ensure we have correct pks
    records = SpotifyEpisode.objects.filter(
        episode_id__in=[item.episode_id for item in items]
    )

    for record in records:
        if not record.podcasts.exists():
            spotifyepisode_auto_assign_podcast(record.id)

    return len(records)
