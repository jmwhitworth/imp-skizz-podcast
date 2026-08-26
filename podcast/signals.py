from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Podcast, YoutubeVideo
from .tasks import podcast_update_title_task, youtubevideo_create_podcast_task


@receiver(post_save, sender=YoutubeVideo)
def youtubevideo_created(sender, instance, created, **kwargs):
    if created:
        youtubevideo_create_podcast_task.enqueue(str(instance.id))


@receiver(post_save, sender=Podcast)
def podcast_created(sender, instance, created, **kwargs):
    if created:
        podcast_update_title_task.enqueue(str(instance.id))
