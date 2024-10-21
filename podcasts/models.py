from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Podcast(models.Model):
    title = models.CharField(max_length=255)
    episode_number = models.IntegerField(unique=True, default=0)
    youtube_id = models.CharField(max_length=50, default="")
    spotify_id = models.CharField(max_length=50, default="")
    release_date = models.DateField()
    tags = models.ManyToManyField(Tag, related_name='podcasts')

    def __str__(self):
        return self.title
    
    def getTags(self):
        return Tag.objects.filter(podcasts__in=[self.id]).distinct()
