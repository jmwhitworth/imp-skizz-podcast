from logging import getLogger

from django.db import transaction

from status.models import StatusModelMixin as Status

from .clients.llm import PodcastEpisodeIdentifier
from .clients.youtube import YoutubeClient
from .models import Podcast, YoutubeVideo

logger = getLogger(__name__)


@transaction.atomic
def youtubevideo_import() -> int:
    client = YoutubeClient()

    items = client.fetch_recent_uploads()

    if not items:
        return 0

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

    return len(records)


def podcast_create_from_youtubevideos() -> int:
    videos = (
        YoutubeVideo.objects.filter(podcasts__isnull=True)
        .not_archived()
        .order_by("published_at")
    )

    if not videos.exists():
        return 0

    logger.info(f"Creating podcasts from {videos.count()} YouTube videos")

    identifier = PodcastEpisodeIdentifier()
    created_count = 0

    for video in videos.iterator():
        logger.info(f"Identifying episode for video: {video.video_id} - {video.title}")
        data = identifier.identify_episode(video.title)
        if data is None or data.season is None or data.episode is None:
            video.status = Status.ARCHIVED
            video.save(update_fields=["status"])
            logger.warning(
                f"Could not identify episode for video: {video.video_id} - {video.title}. Marked as archived."
            )
            continue

        podcast, created = Podcast.objects.get_or_create(
            season=data.season,
            episode=data.episode,
            defaults={
                "title": video.title,
                "release_date": video.published_at.date(),
                "youtube_video": video,
                "status": Status.PUBLISHED,
            },
        )
        if created:
            created_count += 1
            logger.info(
                f"Created podcast: {podcast.title} (Season {podcast.season}, Episode {podcast.episode}) from video: {video.video_id}"
            )
        else:
            video.status = Status.ARCHIVED
            video.save(update_fields=["status"])
            logger.warning(
                f"Podcast already exists for video: {video.video_id} - {video.title}. Marked as archived."
            )

    return created_count
