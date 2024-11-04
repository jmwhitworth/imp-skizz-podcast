from django.contrib import admin
from .models import Podcast

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ["title", "episode_number", "release_date"]
    ordering = ['-release_date', 'episode_number']
    search_fields = ["title"]
    list_filter = ["release_date"]
    date_hierarchy = "release_date"
