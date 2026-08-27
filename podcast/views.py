from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from .models import Podcast


class PodcastView(View):
    def get(self, request, *args, **kwargs):
        # print(request.htmx)

        context = {
            "podcasts": Podcast.objects.published().select_related(
                "youtube_video", "spotify_episode"
            )[
                :6
            ]  # Temp just 6 while developing
        }

        template_content = render_to_string(
            "podcast/index.html", context, request=request
        )
        return HttpResponse(template_content, content_type="text/html")
