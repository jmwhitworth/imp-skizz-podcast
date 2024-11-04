from django.db import models

class Podcast(models.Model):
    title = models.CharField(max_length=255)
    episode_number = models.IntegerField(unique=True, default=0)
    youtube_id = models.CharField(max_length=50, default="")
    spotify_url = models.CharField(max_length=255, blank=True, null=True)
    apple_music_url = models.CharField(max_length=255, blank=True, null=True)
    release_date = models.DateField()
    
    def __str__(self) -> str:
        return self.title
