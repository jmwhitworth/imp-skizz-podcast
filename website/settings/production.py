from .base import *

ENVIRONMENT = "production"

DEBUG = False

ALLOWED_HOSTS = [
    "impandskizzpodcast.com",
    ".impandskizzpodcast.com",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ORIGINS = [
    "https://impandskizzpodcast.com",
    "https://www.impandskizzpodcast.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://impandskizzpodcast.com",
    "https://*.impandskizzpodcast.com",
]

INTERNAL_IPS = [
    "217.154.57.184",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "WARNING"},
}
