import sys, os, django, html

# Load django within this script when ran directly: https://stackoverflow.com/a/31444231
sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "podcast_index.settings")
django.setup()

from podcasts.models import Podcast
from datetime import datetime
import googleapiclient.discovery



print(f"Running at {datetime.now()}") 

