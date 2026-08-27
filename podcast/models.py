from django.db import models

from common.models import BaseModel
from status.models import StatusModelMixin, StatusQuerySet


class PodcastQuerySet(StatusQuerySet):
    def get_queryset(self):
        return super().get_queryset().fetch_mode(models.FETCH_PEERS)


class Podcast(StatusModelMixin, BaseModel):
    objects = PodcastQuerySet.as_manager()

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

    spotify_episode = models.ForeignKey(
        "SpotifyEpisode",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="podcasts",
    )

    # TODO: Apple music

    class Meta:
        verbose_name = "Podcast"
        verbose_name_plural = "Podcasts"
        ordering = ["-release_date", "-season", "-episode"]
        unique_together = ("season", "episode")


class YoutubeVideo(StatusModelMixin, BaseModel):
    objects = StatusQuerySet.as_manager()

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

    @property
    def href(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"

    def __str__(self) -> str:
        return f"{self.title} ({self.video_id})"

    class Meta:
        verbose_name = "YouTube Video"
        verbose_name_plural = "YouTube Videos"
        ordering = ["-published_at", "-id"]


class SpotifyEpisode(StatusModelMixin, BaseModel):
    objects = StatusQuerySet.as_manager()

    episode_id = models.CharField(max_length=255, unique=True, db_index=True)
    release_date = models.DateField()
    duration_ms = models.PositiveIntegerField()
    href = models.URLField(max_length=255, blank=True, null=True)
    preview_url = models.URLField(max_length=255, blank=True, null=True)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    api_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.episode_id})"

    class Meta:
        verbose_name = "Spotify Upload"
        verbose_name_plural = "Spotify Uploads"
        ordering = ["-release_date", "-id"]
