from django.core.management.base import BaseCommand

from podcast.services import spotifyepisode_import, youtubevideo_import


class Command(BaseCommand):
    help = "Imports the recent uploads for the podcast."

    def add_arguments(self, parser):
        parser.add_argument(
            "platform",
            type=str,
            choices=["youtube", "spotify"],
            help="The platform to import recent uploads from (youtube or spotify).",
        )

    def handle(self, *args, **options):
        methods = {
            "youtube": self.import_youtube,
            "spotify": self.import_spotify,
        }
        methods[options["platform"]]()

    def import_youtube(self):
        self.stdout.write(
            self.style.NOTICE("Starting import of recent YouTube uploads.")
        )
        obj_count = youtubevideo_import()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {obj_count} recent YouTube uploads."
            )
        )

    def import_spotify(self):
        self.stdout.write(
            self.style.NOTICE("Starting import of recent Spotify uploads.")
        )
        obj_count = spotifyepisode_import()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {obj_count} recent Spotify uploads."
            )
        )
