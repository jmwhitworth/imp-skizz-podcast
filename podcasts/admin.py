from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Podcast


@admin.register(Podcast)
class PodcastAdmin(ImportExportModelAdmin):
    list_display = ["title", "episode_number", "release_date"]
    ordering = ["-release_date", "episode_number"]
    search_fields = ["title"]
    list_filter = ["release_date"]
    date_hierarchy = "release_date"


class PodcastResource(resources.ModelResource):
    class Meta:
        model = Podcast
