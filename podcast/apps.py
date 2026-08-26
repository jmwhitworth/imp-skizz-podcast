from django.apps import AppConfig


class PodcastConfig(AppConfig):
    name = "podcast"

    def ready(self):
        import podcast.signals
