from django.contrib import admin
from .models import Tag, Podcast

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "podcast_count"]
    search_fields = ["name"]

    def podcast_count(self, obj):
        return obj.podcasts.count()
    podcast_count.short_description = 'Number of Podcasts'

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ["title", "episode_number", "release_date", "tag_count"]
    ordering = ['-release_date', 'episode_number']
    search_fields = ["title"]
    list_filter = ["release_date", "tags"]
    date_hierarchy = "release_date"
    filter_horizontal = ["tags"]

    def tag_count(self, obj):
        return obj.tags.count()
    tag_count.short_description = 'Number of Tags'

