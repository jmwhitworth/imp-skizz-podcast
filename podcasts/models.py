from django.db import models
from django.db.models import Count, Q

class Tag(models.Model):
    name = models.CharField(max_length=255)
    
    
    def __str__(self) -> str:
        return self.name


class Podcast(models.Model):
    title = models.CharField(max_length=255)
    episode_number = models.IntegerField(unique=True, default=0)
    youtube_id = models.CharField(max_length=50, default="")
    spotify_url = models.CharField(max_length=255, blank=True, null=True)
    apple_music_url = models.CharField(max_length=255, blank=True, null=True)
    release_date = models.DateField()
    tags = models.ManyToManyField(Tag, related_name='podcasts', blank=True)
    
    
    def __str__(self) -> str:
        return self.title
    
    
    def allTags(self) -> models.QuerySet:
        """
            Returns all Tags associated to this Podcast
        """
        return Tag.objects.filter(podcasts__in=[self.id]).distinct()
    
    
    def withTheTags(tag_ids:list) -> models.QuerySet:
        """Returns all Podcasts that have all of the given Tag IDs
        
        Args:
            tag_ids (list): A list of IDs belonging to Tags
        """
        return Podcast.objects.annotate(
            matching_tags=Count('tags', filter=Q(tags__id__in=tag_ids), distinct=True)
        ).filter(matching_tags=len(tag_ids)).distinct()
