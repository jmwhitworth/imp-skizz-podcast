#!/bin/sh

# Set container ENV vars to be accessible by CRON
printenv > /etc/environment

# Create CRON's log file so it's immediately available
touch /var/log/cron.log

# Start CRON runner in the background
cron &

# Tail the cron log file with a prefix, in the background
tail -f /var/log/cron.log &

# Apply database migrations
python ./manage.py migrate --no-input

# Collect static files
python ./manage.py collectstatic --no-input

# Start Gunicorn server
exec gunicorn podcast_index.wsgi:application --bind 127.0.0.1:8000
