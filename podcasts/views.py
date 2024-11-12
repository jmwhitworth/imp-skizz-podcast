from .models import Podcast
from django.http import JsonResponse
from django.utils.html import escape
from datetime import timedelta

def get_day_suffix(day):
    """Returns the suffix for a given day of the month."""
    if 11 <= day <= 13:
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

class PodcastView:
    @staticmethod
    def v1_get_podcasts(request):
        """Returns a JSON response of all Podcasts in the database"""
        
        limit = 15
        if request.GET.get('limit'):
            limit = int(escape(request.GET.get('limit')))
        
        page = 1
        if request.GET.get('page'):
            page = int(escape(request.GET.get('page')))
            limit = limit * page
        
        sort = '-episode_number'
        if str(escape(request.GET.get('sort'))) == 'asc':
            sort = 'episode_number'
        
        if request.GET.get('search'):
            search = str(escape(request.GET.get('search')))
            podcasts = Podcast.objects.filter(title__icontains=search).order_by(sort)[:limit]
        else:
            podcasts = Podcast.objects.order_by(sort)[:limit]
        
        podcast_list = list(podcasts.values())
        for podcast in podcast_list:
            day = int(podcast['release_date'].strftime('%d'))
            suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            suffix = get_day_suffix(day)
            day = int(podcast['release_date'].strftime('%d'))
            suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            podcast['formatted_release_date'] = f"{day}{suffix} {podcast['release_date'].strftime('%b %Y')}"
        
        return JsonResponse(podcast_list, safe=False)


    @staticmethod
    def v2_get_podcasts(request):
        """Returns a JSON response of all Podcasts in the database"""
        
        # Limit the number of results returned
        limit = 15
        if request.GET.get('limit'):
            limit = int(escape(request.GET.get('limit')))
        
        # Paginate the results
        page = 1
        if request.GET.get('page'):
            page = int(escape(request.GET.get('page')))
            if page > 1:
                limit = limit * page
        
        # Sort the results
        sort = '-episode_number'
        if str(escape(request.GET.get('sort'))) == 'asc':
            sort = 'episode_number'
        
        # Search by title
        if request.GET.get('search'):
            search = str(escape(request.GET.get('search')))
            podcasts = Podcast.objects.filter(title__icontains=search).order_by(sort)
        else:
            podcasts = Podcast.objects.order_by(sort)
        
        # Trim the results to the limit and convert to a list
        podcast_list = list(podcasts[:limit].values())
        
        for podcast in podcast_list:
            # Format the release date
            podcast['formatted_release_date'] = podcast['release_date'].strftime('%d') + podcast['release_date'].strftime('%d').lstrip('0') + podcast['release_date'].strftime('%B %Y')
            day = int(podcast['release_date'].strftime('%d'))
            suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            podcast['formatted_release_date'] = f"{day}{suffix} {podcast['release_date'].strftime('%b %Y')}"
            
            duration_ms = podcast['duration']
            duration = timedelta(milliseconds=duration_ms)
            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            podcast['formatted_duration'] = f"{hours}:{minutes:02}:{seconds:02}" if hours else f"{minutes}:{seconds:02}"
            
            # Format the duration
            hours, remainder = divmod(duration_ms // 1000, 3600)
        # Strip out fields that are not needed
        fields_to_remove = {'id', 'release_date', 'duration'}
        podcast_list = [
            {key: value for key, value in podcast.items() if key not in fields_to_remove}
            for podcast in podcast_list
        ]

        return JsonResponse({
            "total_results": podcasts.count(),
            "more_results": podcasts.count() > limit,
            "podcasts": podcast_list
        }, safe=False)
