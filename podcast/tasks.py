from django.tasks import task

from .services import podcast_update_title, youtubevideo_create_podcast


@task
def podcast_update_title_task(podcast_id) -> bool:
    return podcast_update_title(podcast_id)


@task
def youtubevideo_create_podcast_task(youtubevideo_id) -> None:
    youtubevideo_create_podcast(youtubevideo_id)
