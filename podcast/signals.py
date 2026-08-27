from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Podcast, SpotifyEpisode, YoutubeVideo
from .tasks import (
    podcast_create_from_youtubevideo_id_task,
    podcast_debrand_title_task,
    spotifyepisode_auto_assign_podcast_task,
)


@receiver(post_save, sender=YoutubeVideo)
def youtubevideo_created(sender, instance, created, **kwargs):
    if created:
        podcast_create_from_youtubevideo_id_task.enqueue(str(instance.id))


@receiver(post_save, sender=Podcast)
def podcast_created(sender, instance, created, **kwargs):
    if created:
        podcast_debrand_title_task.enqueue(str(instance.id))


@receiver(post_save, sender=SpotifyEpisode)
def spotifyepisode_created(sender, instance, created, **kwargs):
    if created:
        spotifyepisode_auto_assign_podcast_task.enqueue(str(instance.id))
