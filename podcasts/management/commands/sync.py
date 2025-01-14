from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Syncs in the latest podcasts from the specified platform."

    def add_arguments(self, parser):
        parser.add_argument("platform", nargs="+", type=str)

    def handle(self, *args, **options):
        valid_platforms = ["youtube", "spotify"]
        
        if len(options["platform"]) > 1:
            raise CommandError("Only one platform can be specified at a time.")
        
        platform = options["platform"][0].lower()
        if platform not in valid_platforms:
            raise CommandError(f"Invalid platform: {platform}")
        
        match platform:
            case "youtube":
                from podcasts.sync.sync import syncYouTube
                syncYouTube()
            case "spotify":
                from podcasts.sync.sync import syncSpotify
                syncSpotify()
