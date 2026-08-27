from django.contrib import admin

from .models import Podcast, SpotifyEpisode, YoutubeVideo
from .tasks import (
    podcast_create_from_youtubevideo_id_task,
    podcast_debrand_title_task,
    spotifyepisode_auto_assign_podcast_task,
)


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ("title", "release_date", "season", "episode", "status")
    list_filter = ("release_date", "status")
    search_fields = ("title",)
    actions = ["debrand_title"]

    @admin.action(description="Debrand selected podcast titles")
    def debrand_title(self, request, queryset):
        for podcast in queryset:
            podcast_debrand_title_task.enqueue(str(podcast.id))


@admin.register(YoutubeVideo)
class YoutubeVideoAdmin(admin.ModelAdmin):
    readonly_fields = ("api_data",)
    list_display = ("title", "video_id", "published_at", "status")
    list_filter = ("published_at", "status")
    search_fields = ("title", "video_id")
    actions = ["create_podcasts"]

    @admin.action(description="Create podcasts for selected")
    def create_podcasts(self, request, queryset):
        for youtube_video in queryset:
            podcast_create_from_youtubevideo_id_task.enqueue(str(youtube_video.id))


@admin.register(SpotifyEpisode)
class SpotifyEpisodeAdmin(admin.ModelAdmin):
    readonly_fields = ("api_data",)
    list_display = ("title", "episode_id", "release_date", "status")
    list_filter = ("release_date", "status")
    search_fields = ("title", "episode_id")
    actions = ["auto_assign_podcasts"]

    @admin.action(description="Auto-assign podcasts for selected Spotify episodes")
    def auto_assign_podcasts(self, request, queryset):
        for spotify_episode in queryset:
            spotifyepisode_auto_assign_podcast_task.enqueue(str(spotify_episode.id))
