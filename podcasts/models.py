from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Podcast(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    tags = models.ManyToManyField(Tag, related_name='podcasts')

    def __str__(self):
        return self.title
