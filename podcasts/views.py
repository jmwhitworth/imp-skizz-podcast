from django.shortcuts import render
from django.db.models import Count
from .models import Podcast, Tag

def index(request):
    tags = Tag.objects.all()
    context = {
        'podcasts': Podcast.objects.all(),
        'tags': tags,
        'applicable_tags': tags,
        'selected_tags': []
    }
    return render(request, 'podcasts/index.html', context)


def filter_podcasts(request):
    # Get a list of all of the selected tag IDs
    tag_ids = request.GET.get('tags', '')
    selected_tags = tag_ids.split(',') if tag_ids else []
    
    # Get the full data set
    tags = Tag.objects.all()
    podcasts = Podcast.objects.all()
    
    # Create default context
    context = {
        'podcasts': podcasts,
        'tags': tags,
        'applicable_tags': tags,
        'selected_tags': selected_tags,
    }
    
    # If no filters, return the default list with all podcasts
    if not selected_tags:
        return render(request, 'podcasts/partials/filter_results.html', context)
    
    # Get the tags for this query
    filtered_tags = Tag.objects.filter(id__in=selected_tags).distinct()
    
    # Filter the podcasts one-by-one using the tags which are selected
    filtered_podcasts = podcasts
    for tag in filtered_tags:
        filtered_podcasts = filtered_podcasts.filter(tags__id__in=[tag.id])
    
    applicable_tags = Tag.objects.filter(podcasts__in=filtered_podcasts).distinct()
    
    context['podcasts'] = filtered_podcasts
    context['applicable_tags'] = applicable_tags
    context['selected_tags'] = filtered_tags
    return render(request, 'podcasts/partials/filter_results.html', context)
    
