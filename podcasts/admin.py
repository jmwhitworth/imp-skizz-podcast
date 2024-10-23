from django.contrib import admin
from .models import Tag, Podcast


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ["title", "episode_number", "release_date"]
    ordering = ['-episode_number']
