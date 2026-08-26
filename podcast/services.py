from logging import getLogger
from typing import Optional

from django.db import transaction

from status.models import StatusModelMixin as Status

from .clients.llm import LLMClient
from .clients.spotify import SpotifyClient
from .clients.youtube import YoutubeClient
from .models import Podcast, SpotifyEpisode, YoutubeVideo

logger = getLogger(__name__)


def podcast_create_from_youtubevideo(youtubevideo: YoutubeVideo) -> Podcast:
    """Creates a podcast entry from a given YouTube video instance."""
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


def podcast_create_from_youtubevideos() -> int:
    """Creates podcast entries from YouTube videos that do not yet have associated podcasts."""
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


def podcast_update_title(podcast_id) -> bool:
    """Updates the title of the given podcast to remove branding and episode identifiers."""
    podcast = Podcast.objects.filter(id=podcast_id).first()
    if not podcast:
        return False

    new_title = LLMClient().rename_episode(podcast.title)

    if new_title != podcast.title:
        podcast.title = new_title
        podcast.save(update_fields=["title"])
        return True
    return False


def youtubevideo_create_podcast(youtubevideo_id) -> Podcast:
    """Creates a podcast entry from a given YouTube video ID."""
    video = YoutubeVideo.objects.filter(id=youtubevideo_id).first()
    if not video:
        return None

    return podcast_create_from_youtubevideo(video)


def youtubevideo_import() -> int:
    """Imports recent YouTube videos and creates corresponding podcast entries."""
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

    podcast_create_from_youtubevideos()

    return len(records)


def spotifyepisode_import() -> int:
    """Imports recent Spotify episodes and creates corresponding podcast entries."""
    items = SpotifyClient().fetch_recent_episodes()

    if not items:
        return 0

    with transaction.atomic():
        records = SpotifyEpisode.objects.bulk_create(
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

    for record in records:
        if not record.podcasts.exists():
            spotifyepisode_assign_podcast(record.id)

    return len(records)


def spotifyepisode_assign_podcast(spotifyepisode_id) -> Optional[Podcast]:
    """Assigns a Spotify episode to a podcast entry."""
    episode = SpotifyEpisode.objects.filter(id=spotifyepisode_id).first()
    if not episode:
        return None

    candidates = Podcast.objects.filter(release_date=episode.release_date)
    podcast = candidates.first() if candidates.count() == 1 else None

    if not podcast:
        data = LLMClient().identify_episode(episode.title)
        if data:
            podcast = Podcast.objects.filter(
                season=data.season, episode=data.episode
            ).first()

    if not podcast:
        return None

    podcast.spotify_episode = episode
    podcast.save(update_fields=["spotify_episode"])
    return podcast
