from django.test import TestCase
from django.urls import reverse
from django.db import models
from .templatetags.podcast_tags import build_tag_filter_url
from .models import Podcast, Tag
from .views import PodcastViews
import datetime

class TemplateTagsTestCase(TestCase):
    def setUp(self):
        self.tagOne = Tag.objects.create(name='Tag One')
        self.tagTwo = Tag.objects.create(name='Tag Two')
        self.tagThree = Tag.objects.create(name='Tag Three')

    def test_build_tag_filter_url_returns_expected(self):
        """That build_tag_filter_url returns expected with valid input"""
        expected = "?tags=%s,%s,%s" % (str(self.tagOne.id), str(self.tagTwo.id), str(self.tagThree.id))
        actual = build_tag_filter_url(self.tagOne.id, [self.tagTwo, self.tagThree])
        
        self.assertIsInstance(actual, str)
        self.assertEqual(expected, actual)
    
    def test_build_tag_filter_url_returns_expected_without_selected_tags(self):
        """The build_tag_filter_url returns expected without providing selected_tags list"""
        expected = "?tags=%s" % (str(self.tagOne.id),)
        actual = build_tag_filter_url(self.tagOne.id)
        
        self.assertIsInstance(actual, str)
        self.assertEqual(expected, actual)
    
    def test_build_tag_filter_url_handles_duplicate_selected_tags(self):
        """The build_tag_filter_url returns expected with duplicate tags in the inputs"""
        expected = "?tags=%s" % (str(self.tagOne.id),)
        actual = build_tag_filter_url(self.tagOne.id, [self.tagOne, self.tagOne])
        
        self.assertIsInstance(actual, str)
        self.assertEqual(expected, actual)
    
    def test_build_tag_filter_url_handles_invalid_input_list_items(self):
        """The build_tag_filter_url handles the selected_tags arg containing invalid items"""
        invalid_inputs = ['foo', 1, None, object(), [], {}]
        expected = "?tags=%s,%s" % (str(self.tagOne.id), str(self.tagTwo.id))
        
        for invalid_input in invalid_inputs:
            with self.subTest(invalid_input=invalid_input):
                actual = build_tag_filter_url(self.tagOne.id, [self.tagTwo, invalid_input])
                self.assertIsInstance(actual, str)
                self.assertEqual(expected, actual)


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
    
    def test_Podcast_allTags_returns_expected(self):
        """That the Podcast.allTags method returns expected"""
        expected = [self.tagOne, self.tagTwo]
        
        self.podcastOne.tags.set(expected)
        
        actual = self.podcastOne.allTags()
        
        self.assertIsInstance(actual, models.QuerySet)
        self.assertQuerySetEqual(list(actual), expected)
        self.assertNotIn(self.tagThree, list(actual))
    
    def test_Podcast_allTags_without_tags(self):
        """Test Podcast.allTags returns expected when the podcast does not have tags"""
        result = self.podcastOne.allTags()
        
        self.assertIsInstance(result, models.QuerySet)
        self.assertQuerySetEqual(list(result), [])
    
    def test_Podcast_withTheTags_returns_expected(self):
        """That the Podcast.withTheTags method returns expected"""
        
        self.podcastOne.tags.set([self.tagOne, self.tagTwo])
        self.podcastTwo.tags.set([self.tagTwo, self.tagThree])
        
        self.assertIsInstance(Podcast.withTheTags([self.tagOne.id]), models.QuerySet)
        self.assertQuerySetEqual(list(Podcast.withTheTags([self.tagOne.id])), [self.podcastOne])
        self.assertQuerySetEqual(list(Podcast.withTheTags([self.tagOne.id, self.tagTwo.id])), [self.podcastOne])
        self.assertQuerySetEqual(list(Podcast.withTheTags([self.tagTwo.id])), [self.podcastOne, self.podcastTwo])
        self.assertQuerySetEqual(list(Podcast.withTheTags([self.tagTwo.id, self.tagThree.id])), [self.podcastTwo])
        self.assertQuerySetEqual(list(Podcast.withTheTags([self.tagOne.id, self.tagThree.id])), [])
    
    def test_Podcast_withTheTags_with_blank_list(self):
        """That Podcast.withTheTags returns expected when given a blank input list"""
        self.assertIsInstance(Podcast.withTheTags([]), models.QuerySet)
        self.assertQuerySetEqual(list(Podcast.withTheTags([])), [])
    
    def test_Podcast_withTheTags_with_duplicates_in_input_list(self):
        """That Podcast.withTheTags handles duplicate Tag ids in the input list"""
        
        self.podcastOne.tags.set([self.tagOne, self.tagTwo])
        self.podcastTwo.tags.set([self.tagTwo, self.tagThree])
        
        result = Podcast.withTheTags([self.tagOne.id, self.tagOne.id])
        
        self.assertIsInstance(result, models.QuerySet)
        self.assertQuerySetEqual(list(result), [self.podcastOne])


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

    def test_PodcastViews_index_renders_correct_template(self):
        """That the index view renders the correct template"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'podcasts/index.html')
        self.assertIn('podcasts', response.context)
        self.assertIsInstance(response.context['podcasts'], models.QuerySet)

    def test_PodcastViews_filter_podcasts_without_tags(self):
        """That filter_podcasts renders all podcasts when no tags are selected"""
        response = self.client.get(reverse('filter_podcasts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'podcasts/partials/filter_results.html')
        self.assertIn('podcasts', response.context)
        self.assertIn('tags', response.context)
        self.assertIsInstance(response.context['podcasts'], models.QuerySet)
        self.assertIsInstance(response.context['tags'], models.QuerySet)
        self.assertEqual(response.context['podcasts'].count(), 2)

    def test_PodcastViews_filter_podcasts_with_tags(self):
        """That filter_podcasts correctly filters podcasts by selected tags"""
        response = self.client.get(reverse('filter_podcasts') + f'?tags={self.tagOne.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'podcasts/partials/filter_results.html')
        self.assertEqual(response.context['podcasts'].count(), 1)
        self.assertEqual(response.context['podcasts'].first(), self.podcastOne)

    def test_PodcastViews_filter_podcasts_with_multiple_tags(self):
        """That filter_podcasts returns podcasts matching all selected tags"""
        response = self.client.get(reverse('filter_podcasts') + f'?tags={self.tagOne.id},{self.tagTwo.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['podcasts'].count(), 1)
        self.assertEqual(response.context['podcasts'].first(), self.podcastOne)

    def test_PodcastViews_filter_podcasts_with_unrelated_tags(self):
        """That filter_podcasts returns no podcasts if no podcasts match the selected tags"""
        unrelated_tag = Tag.objects.create(name='Unrelated Tag')
        response = self.client.get(reverse('filter_podcasts') + f'?tags={unrelated_tag.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['podcasts'].count(), 0)

    def test_PodcastViews__context_returns_expected(self):
        """That _context returns expected data when no arguments are passed"""
        context = PodcastViews._context()
        self.assertIsInstance(context, dict)
        self.assertIn('podcasts', context)
        self.assertIn('tags', context)
        self.assertIsInstance(context['podcasts'], models.QuerySet)
        self.assertIsInstance(context['tags'], models.QuerySet)
        self.assertEqual(context['podcasts'].count(), 2)
        self.assertEqual(context['tags'].count(), 2)

    def test_PodcastViews__context_returns_provided_data(self):
        """That _context returns expected data when podcasts and tags are provided"""
        context = PodcastViews._context(podcasts=[self.podcastOne], tags=[self.tagOne])
        self.assertEqual(len(context['podcasts']), 1)
        self.assertEqual(len(context['tags']), 1)
        self.assertEqual(context['podcasts'][0], self.podcastOne)
        self.assertEqual(context['tags'][0], self.tagOne)
