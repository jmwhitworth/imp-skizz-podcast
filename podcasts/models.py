from django.db import models


class PodcastQuerySet(models.QuerySet):
    def not_archived(self):
        return self.filter(archived=False)


class Podcast(models.Model):
    objects = PodcastQuerySet.as_manager()

    title = models.CharField(max_length=255)
    episode_number = models.PositiveIntegerField(null=True, blank=True)
    youtube_id = models.CharField(max_length=50, default="")
    spotify_url = models.CharField(max_length=255, blank=True, null=True)
    apple_music_url = models.CharField(max_length=255, blank=True, null=True)
    release_date = models.DateField()
    preview_url = models.CharField(max_length=255, blank=True, null=True)
    duration = models.IntegerField(default=0)
    archived = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Podcast"
        verbose_name_plural = "Podcasts"
        ordering = ["-release_date"]
