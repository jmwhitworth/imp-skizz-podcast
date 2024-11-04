from .models import Podcast
from django.http import JsonResponse

class PodcastViews:
    def api_podcasts(request):
        """Returns a JSON response of all Podcasts in the database"""
        podcasts = Podcast.objects.all()
        return JsonResponse(list(podcasts.values()), safe=False)
