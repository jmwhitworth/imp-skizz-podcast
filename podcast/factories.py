import factory
from django.db.models.signals import post_save
from django.utils import timezone

from .models import Podcast, SpotifyEpisode, YoutubeVideo


@factory.django.mute_signals(post_save)
class YoutubeVideoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = YoutubeVideo

    video_id = factory.Sequence(lambda n: f"yt-video-{n}")
    published_at = factory.LazyFunction(timezone.now)
    title = factory.Sequence(lambda n: f"Episode {n} | Imp And Skizz Podcast (Ep{n})")
    description = factory.Faker("sentence")
    api_data = factory.LazyFunction(dict)


@factory.django.mute_signals(post_save)
class SpotifyEpisodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpotifyEpisode

    episode_id = factory.Sequence(lambda n: f"spotify-episode-{n}")
    release_date = factory.LazyFunction(lambda: timezone.now().date())
    duration_ms = 3_600_000
    href = factory.Sequence(lambda n: f"https://open.spotify.com/episode/{n}")
    preview_url = factory.Sequence(lambda n: f"https://p.scdn.co/mp3-preview/{n}")
    title = factory.Sequence(lambda n: f"Episode {n}")
    description = factory.Faker("sentence")
    api_data = factory.LazyFunction(dict)


@factory.django.mute_signals(post_save)
class PodcastFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Podcast

    title = factory.Sequence(lambda n: f"Episode {n}")
    release_date = factory.LazyFunction(lambda: timezone.now().date())
    season = 1
    episode = factory.Sequence(lambda n: n + 1)
