#!/bin/sh
# Add CRON and Python locations to PATH
PATH="$PATH:/usr/sbin"

# Start CRON runner in background
cron &

# Apply database migrations
python ./manage.py migrate --no-input

# Collect static files
python ./manage.py collectstatic --no-input

# Start Gunicorn server
gunicorn podcast_index.wsgi:application --bind 0.0.0.0:8000