# Imp & Skizz Podcast Index

This is the backend portion of the following project: [impandskizzpodcast.com](https://impandskizzpodcast.com/)

You can see the NUXT frontend here: [https://github.com/jmwhitworth/imp-skizz-podcast-frontend](https://github.com/jmwhitworth/imp-skizz-podcast-frontend)


# Installation

## Python

To install, use `pipenv`:
```bash
pipenv install
```

To then run the project locally:
```bash
# To use the installed Python environment
pipenv shell

python manage.js runserver
```

## Node

To install, use NPM:
```bash
npm install
```

> Node version `21` required.

To watch for changes:
```bash
npm run start
```

To build for production:
```bash
npm run build
```

## Others

To fix template indentation:
```bash
djhtml ./podcasts/templates/podcasts/**/*.html
```

## Sync

A syncing script is set up to fetch the latest YouTube and Spotify uploads. This is ran via CRON at 15:00 daily.

For this to work, the following environment variables must be present:

### YouTube:
- `YOUTUBE_API_KEY`
- `YOUTUBE_CHANNEL_ID`

### Spotify
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `SPOTIFY_SHOW_ID`

The sync runs via the `jobs/sync.py` file.
