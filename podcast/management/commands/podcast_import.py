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

        parser.add_argument(
            "--all",
            action="store_true",
            help="Import all available uploads instead of only recent ones.",
        )

    def handle(self, *args, **options):
        methods = {
            "youtube": self.import_youtube,
            "spotify": self.import_spotify,
        }
        return methods[options["platform"]](all=options["all"])

    def import_youtube(self, all: bool = False):
        self.stdout.write(
            self.style.NOTICE("Starting import of recent YouTube uploads.")
        )
        obj_count = youtubevideo_import(all=all)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {obj_count} recent YouTube uploads."
            )
        )

    def import_spotify(self, all: bool = False):
        self.stdout.write(
            self.style.NOTICE("Starting import of recent Spotify uploads.")
        )
        obj_count = spotifyepisode_import(all=all)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {obj_count} recent Spotify uploads."
            )
        )
