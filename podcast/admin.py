from django.contrib import admin

from .models import Podcast, YoutubeVideo


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ("title", "release_date", "season", "episode", "status")
    list_filter = ("status",)
    search_fields = ("title",)


@admin.register(YoutubeVideo)
class YoutubeVideoAdmin(admin.ModelAdmin):
    readonly_fields = ("api_data",)
    list_display = ("title", "video_id", "published_at")
    list_filter = ("published_at",)
    search_fields = ("title", "video_id")
