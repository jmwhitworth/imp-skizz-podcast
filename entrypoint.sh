#!/bin/sh

printenv > /etc/environment
python ./manage.py migrate --no-input
python ./manage.py collectstatic --no-input
exec gunicorn podcast_index.wsgi:application --bind 0.0.0.0:8000
