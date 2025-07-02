#!/bin/sh

python ./manage.py migrate --no-input

exec gunicorn podcast_index.wsgi:application --bind 0.0.0.0:8000 --access-logfile -
