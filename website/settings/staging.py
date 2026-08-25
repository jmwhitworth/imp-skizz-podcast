import os

from .base import *

ENVIRONMENT = "staging"

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = []

INTERNAL_IPS = []
