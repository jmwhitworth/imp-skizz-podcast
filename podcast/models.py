from django.db import models

from common.models import BaseModel
from status.models import StatusModelMixin


class Podcast(StatusModelMixin, BaseModel):
    title = models.CharField(max_length=255)
    release_date = models.DateField()

    season = models.PositiveIntegerField()
    episode = models.PositiveIntegerField()

    youtube_video = models.ForeignKey(
        "YoutubeVideo",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="podcasts",
    )

    # spotify_url = models.URLField(max_length=255, blank=True, null=True)
    # spotify_preview_url = models.URLField(max_length=255, blank=True, null=True)

    # apple_music_url = models.URLField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Podcast"
        verbose_name_plural = "Podcasts"
        ordering = ["-release_date", "-season", "-episode"]
        unique_together = ("season", "episode")


class YoutubeVideo(BaseModel):
    video_id = models.CharField(max_length=255, unique=True, db_index=True)
    published_at = models.DateTimeField()

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    api_data = models.JSONField(blank=True, null=True)

    @property
    def thumbnail_default(self) -> str:
        return f"https://i.ytimg.com/vi/{self.video_id}/default.jpg"

    @property
    def thumbnail_medium(self) -> str:
        return f"https://i.ytimg.com/vi/{self.video_id}/mqdefault.jpg"

    @property
    def thumbnail_high(self) -> str:
        return f"https://i.ytimg.com/vi/{self.video_id}/hqdefault.jpg"

    def __str__(self) -> str:
        return f"{self.title} ({self.video_id})"

    class Meta:
        verbose_name = "YouTube Video"
        verbose_name_plural = "YouTube Videos"
        ordering = ["-published_at"]
