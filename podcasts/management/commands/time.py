from django.core.management.base import BaseCommand
from datetime import datetime
from podcasts.sync.helpers import log

class Command(BaseCommand):
    help = "Shows the current time. Used for showing CRON is running."

    def handle(self, *args, **options):
        log(f"Running at {datetime.now()}", "print_time")
