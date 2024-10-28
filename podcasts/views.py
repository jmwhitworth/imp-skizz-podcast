from django.shortcuts import render
from .models import Podcast, Tag

class PodcastViews:
    def index(request):
        return render(request, 'podcasts/index.html', PodcastViews._context())
    
    def filter_podcasts(request):
        """
            Uses the 'tags' and renders only the Podcasts with the given Tag IDs
        """
        context = PodcastViews._context()
        
        selected_tags_string = request.GET.get('tags')
        
        if not selected_tags_string:
            return render(request, 'podcasts/partials/filter_results.html', context)
        
        selected_tags_ids = selected_tags_string.split(',') if selected_tags_string else []
        selected_tags = Tag.objects.filter(id__in=selected_tags_ids).distinct()
        
        # Annotate podcasts with the count of matching tags and filter by the number of selected tags
        filtered_podcasts = Podcast.withTheTags(selected_tags_ids).order_by('-episode_number')
        
        applicable_tags = Tag.objects.filter(podcasts__in=filtered_podcasts).distinct()
        
        context['podcasts'] = filtered_podcasts
        context['applicable_tags'] = applicable_tags
        context['selected_tags'] = selected_tags
        return render(request, 'podcasts/partials/filter_results.html', context)
    
    @staticmethod
    def _context(podcasts=None, tags=None) -> dict:
        """Provides the default context dictionary to be passed to the page render.
        If no Podcasts or Tags are provided, all are queries from the database and used.
        
        Args:
            podcasts (django.db.models.QuerySet, optional): The Podcasts to assign to the dictionary. Defaults to None.
            tags (django.db.models.QuerySet, optional): The Tags to assign to the dictionary. Defaults to None.
        
        Returns:
            dict: The default dictionary of data for the page renderer
        """
        p = podcasts if podcasts is not None else Podcast.objects.all().order_by('-episode_number')
        t = tags if tags is not None else Tag.objects.all()
        return {
            'podcasts': p,
            'tags': t,
            'applicable_tags': t,
            'selected_tags': []
        }
