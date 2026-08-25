from django.db import transaction

from .clients.youtube import YoutubeClient
from .models import Podcast, YoutubeVideo


@transaction.atomic
def youtube_import() -> int:
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
            )
            for item in items
        ],
        update_conflicts=True,
        unique_fields=["video_id"],
        update_fields=["title", "description", "api_data"],
    )

    return len(records)
