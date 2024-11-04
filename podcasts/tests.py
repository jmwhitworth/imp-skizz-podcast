from django.test import TestCase
from django.urls import reverse
from django.db import models
from .models import Podcast, Tag
import datetime

class TemplateTagsTestCase(TestCase):
    def setUp(self):
        self.tagOne = Tag.objects.create(name='Tag One')
        self.tagTwo = Tag.objects.create(name='Tag Two')
        self.tagThree = Tag.objects.create(name='Tag Three')


class TagTestCase(TestCase):
    def test_Tag__str__returns_name(self):
        """That the __str__ of the instance returns the name"""
        expected = "foo"
        tag = Tag.objects.create(name = expected)
        self.assertEqual(str(tag), expected)


class PodcastTestCase(TestCase):
    def setUp(self):
        self.tagOne = Tag.objects.create(name='Tag One')
        self.tagTwo = Tag.objects.create(name='Tag Two')
        self.tagThree = Tag.objects.create(name='Tag Three')
        self.podcastOne = Podcast.objects.create(
            title='Podcast One',
            episode_number=1,
            youtube_id='foo',
            release_date=datetime.date.today()
        )
        self.podcastTwo = Podcast.objects.create(
            title='Podcast Two',
            episode_number=2,
            youtube_id='bar',
            release_date=datetime.date.today()
        )
    
    def test_Podcast__str__returns_title(self):
        """That the __str__ of the instance returns the title"""
        self.assertEqual(str(self.podcastOne), 'Podcast One')


class ViewsTestCase(TestCase):
    def setUp(self):
        self.tagOne = Tag.objects.create(name='Tag One')
        self.tagTwo = Tag.objects.create(name='Tag Two')
        self.podcastOne = Podcast.objects.create(
            title='Podcast One',
            episode_number=1,
            youtube_id='foo',
            release_date=datetime.date.today()
        )
        self.podcastOne.tags.add(self.tagOne, self.tagTwo)
        
        self.podcastTwo = Podcast.objects.create(
            title='Podcast Two',
            episode_number=2,
            youtube_id='bar',
            release_date=datetime.date.today()
        )
        self.podcastTwo.tags.add(self.tagTwo)
