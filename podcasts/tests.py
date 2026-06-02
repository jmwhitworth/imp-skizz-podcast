import json
from datetime import date

from django.test import RequestFactory, TestCase
from factory import Faker
from factory.django import DjangoModelFactory

from podcasts.models import Podcast
from podcasts.views import PodcastView


class PodcastFactory(DjangoModelFactory):
    class Meta:
        model = Podcast

    title = Faker("sentence", nb_words=4)
    episode_number = Faker("random_int", min=1, max=100)
    release_date = Faker("date")
    preview_url = Faker("url")
    duration = Faker("random_int", min=1, max=3600)


class PodcastModelTestCase(TestCase):
    def test_podcast_creation(self):
        podcast = PodcastFactory()
        self.assertIsInstance(podcast, Podcast)
        self.assertTrue(podcast.title)
        self.assertTrue(podcast.episode_number)
        self.assertTrue(podcast.release_date)
        self.assertTrue(podcast.duration)

    def test_podcast_str_method(self):
        podcast = PodcastFactory(title="Test Podcast")
        self.assertEqual(str(podcast), "Test Podcast")


class V2PodcastViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _get(self, **params):
        request = self.factory.get("/api/v2/podcasts", params)
        return PodcastView.v2_get_podcasts(request)

    def _json(self, response):
        return json.loads(response.content)

    def _make_podcasts(self, count):
        return [PodcastFactory(episode_number=i + 1) for i in range(count)]

    # --- Response structure ---

    def test_response_structure(self):
        PodcastFactory(episode_number=1)
        data = self._json(self._get())
        self.assertIn("total_results", data)
        self.assertIn("more_results", data)
        self.assertIn("podcasts", data)

    def test_empty_database(self):
        data = self._json(self._get())
        self.assertEqual(data["total_results"], 0)
        self.assertFalse(data["more_results"])
        self.assertEqual(data["podcasts"], [])

    # --- Limit ---

    def test_default_limit_is_15(self):
        self._make_podcasts(20)
        data = self._json(self._get())
        self.assertEqual(len(data["podcasts"]), 15)

    def test_custom_limit(self):
        self._make_podcasts(10)
        data = self._json(self._get(limit=5))
        self.assertEqual(len(data["podcasts"]), 5)

    def test_limit_clamped_to_min_one(self):
        self._make_podcasts(5)
        data = self._json(self._get(limit=0))
        self.assertEqual(len(data["podcasts"]), 1)

    def test_limit_clamped_to_max_100(self):
        self._make_podcasts(10)
        data = self._json(self._get(limit=200))
        self.assertEqual(len(data["podcasts"]), 10)

    # --- Pagination ---

    def test_page_2_doubles_limit(self):
        self._make_podcasts(20)
        data = self._json(self._get(limit=5, page=2))
        self.assertEqual(len(data["podcasts"]), 10)

    def test_page_1_behaves_same_as_default(self):
        self._make_podcasts(20)
        self.assertEqual(
            len(self._json(self._get())["podcasts"]),
            len(self._json(self._get(page=1))["podcasts"]),
        )

    # --- Sorting ---

    def test_default_sort_is_descending_by_episode_number(self):
        for ep in [1, 2, 3]:
            PodcastFactory(episode_number=ep)
        episodes = [p["episode_number"] for p in self._json(self._get())["podcasts"]]
        self.assertEqual(episodes, sorted(episodes, reverse=True))

    def test_sort_ascending(self):
        for ep in [1, 2, 3]:
            PodcastFactory(episode_number=ep)
        episodes = [p["episode_number"] for p in self._json(self._get(sort="asc"))["podcasts"]]
        self.assertEqual(episodes, sorted(episodes))

    # --- Search ---

    def test_search_filters_by_title(self):
        PodcastFactory(episode_number=1, title="Alpha Episode")
        PodcastFactory(episode_number=2, title="Beta Episode")
        PodcastFactory(episode_number=3, title="Gamma Episode")
        data = self._json(self._get(search="Alpha"))
        self.assertEqual(len(data["podcasts"]), 1)
        self.assertIn("Alpha", data["podcasts"][0]["title"])

    def test_search_is_case_insensitive(self):
        PodcastFactory(episode_number=1, title="Alpha Episode")
        data = self._json(self._get(search="alpha"))
        self.assertEqual(data["total_results"], 1)

    def test_search_returns_empty_when_no_match(self):
        PodcastFactory(episode_number=1, title="Alpha Episode")
        data = self._json(self._get(search="nonexistent"))
        self.assertEqual(data["total_results"], 0)
        self.assertEqual(data["podcasts"], [])

    def test_total_results_reflects_search_count(self):
        PodcastFactory(episode_number=1, title="Alpha Episode")
        PodcastFactory(episode_number=2, title="Beta Episode")
        PodcastFactory(episode_number=3, title="Alpha Special")
        data = self._json(self._get(search="Alpha"))
        self.assertEqual(data["total_results"], 2)

    # --- Pagination metadata ---

    def test_more_results_true_when_results_exceed_limit(self):
        self._make_podcasts(20)
        self.assertTrue(self._json(self._get(limit=5))["more_results"])

    def test_more_results_false_when_all_results_fit(self):
        self._make_podcasts(3)
        self.assertFalse(self._json(self._get(limit=10))["more_results"])

    def test_total_results_reflects_full_unsliced_count(self):
        self._make_podcasts(7)
        data = self._json(self._get(limit=3))
        self.assertEqual(data["total_results"], 7)

    # --- Field stripping ---

    def test_id_field_stripped_from_response(self):
        PodcastFactory(episode_number=1)
        for podcast in self._json(self._get())["podcasts"]:
            self.assertNotIn("id", podcast)

    def test_release_date_field_stripped_from_response(self):
        PodcastFactory(episode_number=1)
        for podcast in self._json(self._get())["podcasts"]:
            self.assertNotIn("release_date", podcast)

    def test_duration_field_stripped_from_response(self):
        PodcastFactory(episode_number=1)
        for podcast in self._json(self._get())["podcasts"]:
            self.assertNotIn("duration", podcast)

    # --- Formatted release date ---

    def test_formatted_release_date_st_suffix(self):
        PodcastFactory(episode_number=1, release_date=date(2024, 3, 1))
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_release_date"], "1st Mar 2024")

    def test_formatted_release_date_nd_suffix(self):
        PodcastFactory(episode_number=1, release_date=date(2024, 3, 2))
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_release_date"], "2nd Mar 2024")

    def test_formatted_release_date_rd_suffix(self):
        PodcastFactory(episode_number=1, release_date=date(2024, 3, 3))
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_release_date"], "3rd Mar 2024")

    def test_formatted_release_date_th_suffix(self):
        PodcastFactory(episode_number=1, release_date=date(2024, 3, 4))
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_release_date"], "4th Mar 2024")

    def test_formatted_release_date_11th_exception(self):
        PodcastFactory(episode_number=1, release_date=date(2024, 3, 11))
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_release_date"], "11th Mar 2024")

    def test_formatted_release_date_12th_exception(self):
        PodcastFactory(episode_number=1, release_date=date(2024, 3, 12))
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_release_date"], "12th Mar 2024")

    def test_formatted_release_date_13th_exception(self):
        PodcastFactory(episode_number=1, release_date=date(2024, 3, 13))
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_release_date"], "13th Mar 2024")

    def test_formatted_release_date_21st(self):
        PodcastFactory(episode_number=1, release_date=date(2024, 3, 21))
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_release_date"], "21st Mar 2024")

    def test_formatted_release_date_22nd(self):
        PodcastFactory(episode_number=1, release_date=date(2024, 3, 22))
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_release_date"], "22nd Mar 2024")

    def test_formatted_release_date_23rd(self):
        PodcastFactory(episode_number=1, release_date=date(2024, 3, 23))
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_release_date"], "23rd Mar 2024")

    # --- Formatted duration ---

    def test_formatted_duration_minutes_and_seconds(self):
        PodcastFactory(episode_number=1, duration=90000)  # 1m 30s
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_duration"], "1:30")

    def test_formatted_duration_seconds_only(self):
        PodcastFactory(episode_number=1, duration=45000)  # 45s
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_duration"], "0:45")

    def test_formatted_duration_with_hours(self):
        PodcastFactory(episode_number=1, duration=3661000)  # 1h 1m 1s
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_duration"], "1:01:01")

    def test_formatted_duration_exact_one_hour(self):
        PodcastFactory(episode_number=1, duration=3600000)  # 1h 0m 0s
        data = self._json(self._get())
        self.assertEqual(data["podcasts"][0]["formatted_duration"], "1:00:00")
