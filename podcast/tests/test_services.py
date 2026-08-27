import uuid
from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from status.models import StatusModelMixin as Status

from ..clients.llm import EpisodeIdentityData
from ..clients.spotify import RemoteEpisode
from ..clients.youtube import RemoteVideo
from ..factories import PodcastFactory, SpotifyEpisodeFactory, YoutubeVideoFactory
from ..models import Podcast, SpotifyEpisode, YoutubeVideo
from ..services import (
    podcast_create_for_all_youtubevideos,
    podcast_create_from_youtubevideo,
    podcast_create_from_youtubevideo_id,
    podcast_debrand_title,
    spotifyepisode_auto_assign_podcast,
    spotifyepisode_import,
    youtubevideo_import,
)


@patch("podcast.services.LLMClient")
class services__podcast_create_from_youtubevideo__TestCase(TestCase):
    def test_creates_podcast_when_episode_identified(self, mock_llm_client):
        mock_llm_client.return_value.identify_episode.return_value = (
            EpisodeIdentityData(reasoning="test", is_episode=True, season=2, episode=7)
        )
        mock_llm_client.return_value.rename_episode.side_effect = lambda title: title
        video = YoutubeVideoFactory(title="Some Episode (S2Ep7)")

        podcast = podcast_create_from_youtubevideo(video)

        self.assertIsNotNone(podcast)
        self.assertEqual(podcast.season, 2)
        self.assertEqual(podcast.episode, 7)
        self.assertEqual(podcast.title, video.title)
        self.assertEqual(podcast.release_date, video.published_at.date())
        self.assertEqual(podcast.youtube_video_id, video.id)
        self.assertTrue(podcast.is_published)

    def test_archives_video_when_not_identified_as_episode(self, mock_llm_client):
        mock_llm_client.return_value.identify_episode.return_value = None
        video = YoutubeVideoFactory()

        podcast = podcast_create_from_youtubevideo(video)

        self.assertIsNone(podcast)
        video.refresh_from_db()
        self.assertTrue(video.is_archived)

    def test_archives_video_when_podcast_already_exists_for_season_episode(
        self, mock_llm_client
    ):
        mock_llm_client.return_value.identify_episode.return_value = (
            EpisodeIdentityData(reasoning="test", is_episode=True, season=1, episode=3)
        )
        existing = PodcastFactory(season=1, episode=3)
        video = YoutubeVideoFactory()

        podcast = podcast_create_from_youtubevideo(video)

        self.assertEqual(podcast, existing)
        video.refresh_from_db()
        self.assertTrue(video.is_archived)


@patch("podcast.services.LLMClient")
class services__podcast_create_for_all_youtubevideos__TestCase(TestCase):
    def test_creates_podcasts_for_unlinked_non_archived_videos(self, mock_llm_client):
        mock_llm_client.return_value.identify_episode.side_effect = [
            EpisodeIdentityData(reasoning="", is_episode=True, season=1, episode=1),
            EpisodeIdentityData(reasoning="", is_episode=True, season=1, episode=2),
        ]
        mock_llm_client.return_value.rename_episode.side_effect = lambda title: title
        now = timezone.now()
        YoutubeVideoFactory(title="Ep 1", published_at=now - timedelta(days=2))
        YoutubeVideoFactory(title="Ep 2", published_at=now - timedelta(days=1))
        YoutubeVideoFactory(status=Status.ARCHIVED, published_at=now)

        created_count = podcast_create_for_all_youtubevideos()

        self.assertEqual(created_count, 2)
        self.assertEqual(Podcast.objects.count(), 2)

    def test_returns_zero_when_no_eligible_videos(self, mock_llm_client):
        created_count = podcast_create_for_all_youtubevideos()

        self.assertEqual(created_count, 0)
        mock_llm_client.return_value.identify_episode.assert_not_called()


class services__podcast_debrand_title__TestCase(TestCase):
    def test_returns_false_when_podcast_not_found(self):
        self.assertFalse(podcast_debrand_title(uuid.uuid4()))

    @patch("podcast.services.LLMClient")
    def test_updates_title_when_renamed(self, mock_llm_client):
        mock_llm_client.return_value.rename_episode.return_value = "Clean Title"
        podcast = PodcastFactory(title="Messy Title | Branding (S1Ep1)")

        result = podcast_debrand_title(podcast.id)

        self.assertTrue(result)
        podcast.refresh_from_db()
        self.assertEqual(podcast.title, "Clean Title")

    @patch("podcast.services.LLMClient")
    def test_returns_false_when_title_unchanged(self, mock_llm_client):
        mock_llm_client.return_value.rename_episode.return_value = "Same Title"
        podcast = PodcastFactory(title="Same Title")

        result = podcast_debrand_title(podcast.id)

        self.assertFalse(result)
        podcast.refresh_from_db()
        self.assertEqual(podcast.title, "Same Title")


@patch("podcast.services.LLMClient")
class services__podcast_create_from_youtubevideo_id__TestCase(TestCase):
    def test_returns_none_when_video_not_found(self, mock_llm_client):
        self.assertIsNone(podcast_create_from_youtubevideo_id(uuid.uuid4()))
        mock_llm_client.return_value.identify_episode.assert_not_called()

    def test_creates_podcast_for_existing_video(self, mock_llm_client):
        mock_llm_client.return_value.identify_episode.return_value = (
            EpisodeIdentityData(reasoning="", is_episode=True, season=1, episode=9)
        )
        mock_llm_client.return_value.rename_episode.side_effect = lambda title: title
        video = YoutubeVideoFactory()

        podcast = podcast_create_from_youtubevideo_id(video.id)

        self.assertIsNotNone(podcast)
        self.assertEqual(podcast.episode, 9)


@patch("podcast.services.YoutubeClient")
@patch("podcast.services.LLMClient")
class services__youtubevideo_import__TestCase(TestCase):
    def test_returns_zero_when_no_items(self, mock_llm_client, mock_youtube_client):
        mock_youtube_client.return_value.fetch_recent_uploads.return_value = []

        self.assertEqual(youtubevideo_import(), 0)

    def test_imports_videos_and_creates_podcasts(
        self, mock_llm_client, mock_youtube_client
    ):
        mock_llm_client.return_value.identify_episode.return_value = (
            EpisodeIdentityData(reasoning="", is_episode=True, season=1, episode=42)
        )
        mock_llm_client.return_value.rename_episode.side_effect = lambda title: title
        mock_youtube_client.return_value.fetch_recent_uploads.return_value = [
            RemoteVideo(
                id="yt-1",
                publishedAt=timezone.now(),
                title="New Episode (Ep42)",
                description="desc",
                api_data={},
            )
        ]

        imported_count = youtubevideo_import()

        self.assertEqual(imported_count, 1)
        self.assertTrue(YoutubeVideo.objects.filter(video_id="yt-1").exists())
        self.assertTrue(Podcast.objects.filter(season=1, episode=42).exists())


@patch("podcast.services.SpotifyClient")
@patch("podcast.services.spotifyepisode_auto_assign_podcast")
class services__spotifyepisode_import__TestCase(TestCase):
    def test_returns_zero_when_no_items(self, mock_assign, mock_spotify_client):
        mock_spotify_client.return_value.fetch_recent_episodes.return_value = []

        self.assertEqual(spotifyepisode_import(), 0)
        mock_assign.assert_not_called()

    def test_persists_preview_url_and_assigns_new_episodes(
        self, mock_assign, mock_spotify_client
    ):
        mock_spotify_client.return_value.fetch_recent_episodes.return_value = [
            RemoteEpisode(
                episode_id="sp-1",
                release_date=date(2024, 1, 1),
                duration_ms=1000,
                href="https://open.spotify.com/episode/sp-1",
                title="Episode One",
                description="desc",
                preview_url="https://p.scdn.co/mp3-preview/sp-1",
                api_data={},
            )
        ]

        imported_count = spotifyepisode_import()

        self.assertEqual(imported_count, 1)
        episode = SpotifyEpisode.objects.get(episode_id="sp-1")
        self.assertEqual(episode.preview_url, "https://p.scdn.co/mp3-preview/sp-1")
        mock_assign.assert_called_once_with(episode.id)

    def test_skips_assignment_for_episodes_already_linked_to_a_podcast(
        self, mock_assign, mock_spotify_client
    ):
        episode = SpotifyEpisodeFactory(episode_id="sp-2")
        PodcastFactory(spotify_episode=episode)

        mock_spotify_client.return_value.fetch_recent_episodes.return_value = [
            RemoteEpisode(
                episode_id="sp-2",
                release_date=episode.release_date,
                duration_ms=episode.duration_ms,
                href=episode.href,
                title=episode.title,
                description=episode.description,
                preview_url=episode.preview_url,
                api_data={},
            )
        ]

        spotifyepisode_import()

        mock_assign.assert_not_called()


class services__spotifyepisode_auto_assign_podcast__TestCase(TestCase):
    def test_returns_none_when_episode_not_found(self):
        self.assertIsNone(spotifyepisode_auto_assign_podcast(uuid.uuid4()))

    def test_matches_unique_release_date(self):
        podcast = PodcastFactory(release_date=date(2024, 3, 1))
        episode = SpotifyEpisodeFactory(release_date=date(2024, 3, 1))

        result = spotifyepisode_auto_assign_podcast(episode.id)

        self.assertEqual(result, podcast)
        podcast.refresh_from_db()
        self.assertEqual(podcast.spotify_episode, episode)

    @patch("podcast.services.LLMClient")
    def test_returns_none_when_no_match_found(self, mock_llm_client):
        mock_llm_client.return_value.identify_episode.return_value = None
        episode = SpotifyEpisodeFactory(release_date=date(2024, 3, 1))

        result = spotifyepisode_auto_assign_podcast(episode.id)

        self.assertIsNone(result)
