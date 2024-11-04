from django.shortcuts import render
from .models import Podcast, Tag
from django.http import JsonResponse
from django.db.models import Count

class PodcastViews:
    def api_podcasts(request):
        """Returns a JSON response of all Podcasts in the database, including related tags"""
        tags_name = request.GET.getlist('tags')
        print(tags_name)
        
        if tags_name:
            podcasts = Podcast.objects.filter(tags__name__in=tags_name).distinct()
        else:
            podcasts = Podcast.objects.all()
        
        podcasts_data = []
        for podcast in podcasts:
            podcast_data = {
                'id': podcast.id,
                'title': podcast.title,
                'episode_number': podcast.episode_number,
                'tags': list(podcast.tags.values('id', 'name'))
            }
            podcasts_data.append(podcast_data)
        
        return JsonResponse(podcasts_data, safe=False)
    
    def api_tags(request):
        """Returns a JSON response of all Tags in the database with the count of related podcasts"""
        tags = Tag.objects.annotate(podcast_count=Count('podcasts'))
        tags_data = list(tags.values('id', 'name', 'podcast_count'))
        return JsonResponse(tags_data, safe=False)
