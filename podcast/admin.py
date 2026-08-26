from django.contrib import admin

from .models import Podcast, SpotifyEpisode, YoutubeVideo


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ("title", "release_date", "season", "episode", "status")
    list_filter = ("release_date", "status")
    search_fields = ("title",)


@admin.register(YoutubeVideo)
class YoutubeVideoAdmin(admin.ModelAdmin):
    readonly_fields = ("api_data",)
    list_display = ("title", "video_id", "published_at", "status")
    list_filter = ("published_at", "status")
    search_fields = ("title", "video_id")


@admin.register(SpotifyEpisode)
class SpotifyEpisodeAdmin(admin.ModelAdmin):
    readonly_fields = ("api_data",)
    list_display = ("title", "episode_id", "release_date", "status")
    list_filter = ("release_date", "status")
    search_fields = ("title", "episode_id")
