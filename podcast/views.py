from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from .models import Podcast
from .selectors import podcast_get_season_numbers


class PodcastView(View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get("search", "")
        season_query = request.GET.get("season", "all")

        podcasts = Podcast.objects.published().select_related(
            "youtube_video", "spotify_episode"
        )

        if search_query:
            podcasts = podcasts.filter(title__icontains=search_query)
        if season_query != "all":
            podcasts = podcasts.filter(season=season_query)

        template = "podcast/index.html"
        if request.htmx:
            template = "podcast/podcast_grid.html"

        template_content = render_to_string(
            template,
            {
                "podcasts": podcasts,
                "season_numbers": podcast_get_season_numbers(),
            },
            request=request,
        )
        return HttpResponse(template_content, content_type="text/html")
