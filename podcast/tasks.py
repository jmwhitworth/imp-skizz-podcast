from django.tasks import task

from .services import (
    podcast_create_from_youtubevideo_id,
    podcast_debrand_title,
    spotifyepisode_auto_assign_podcast,
)


@task
def podcast_create_from_youtubevideo_id_task(youtubevideo_id) -> None:
    podcast_create_from_youtubevideo_id(youtubevideo_id)


@task
def podcast_debrand_title_task(podcast_id) -> None:
    podcast_debrand_title(podcast_id)


@task
def spotifyepisode_auto_assign_podcast_task(spotifyepisode_id) -> None:
    spotifyepisode_auto_assign_podcast(spotifyepisode_id)
