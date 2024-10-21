from django.shortcuts import render
from django.http import HttpResponse
from .models import Podcast, Tag

def index(request):
    podcasts = Podcast.objects.all()
    tags = Tag.objects.all()
    return render(request, 'podcasts/index.html', {'podcasts': podcasts, 'tags': tags})

def filter_podcasts(request):
    tag_id = request.GET.get('tag')
    selected_tag = Tag.objects.get(id=tag_id)
    podcasts = Podcast.objects.filter(tags=selected_tag)
    return render(request, 'podcasts/partials/podcast_list.html', {'podcasts': podcasts})
