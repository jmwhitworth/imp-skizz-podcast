# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Backend API for the [Imp & Skizz Podcast](https://impandskizzpodcast.com/) — a Django REST API that serves podcast episode data to a separate Nuxt frontend. The API reads from a MySQL database and exposes two versioned endpoints. A sync system fetches new episodes from YouTube and Spotify.

## Commands

### Local Development

```bash
# Install dependencies
poetry install

# Run dev server (requires DATABASE_URL env var)
python manage.py runserver

# Apply migrations
python manage.py migrate

# Run sync for a specific platform
python manage.py sync youtube
python manage.py sync spotify

# Format code
black .
isort .
```

### Docker

```bash
# Build and run via docker-compose (production-like)
docker-compose up --build
```

The compose file connects to an external `dokploy-network` for Traefik routing — ports are not exposed directly.

## Environment Variables

Copy `.env.sample` to `.env`. Required variables:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | MySQL connection string (`mysql://user:pass@host:port/db`) |
| `ENVIRONMENT` | Set to `local` to disable HTTPS for OAuth |
| `YOUTUBE_API_KEY` | Google API key for YouTube Data API v3 |
| `YOUTUBE_CHANNEL_ID` | YouTube channel ID to sync from |
| `SPOTIFY_CLIENT_ID` | Spotify app client ID |
| `SPOTIFY_CLIENT_SECRET` | Spotify app client secret |
| `SPOTIFY_SHOW_ID` | Spotify show ID to sync from |

## Architecture

### API Layer

- `podcast_index/urls.py` → root routing, mounts `podcasts.urls`
- `podcasts/urls.py` → two endpoints: `GET /api/v1/podcasts` and `GET /api/v2/podcasts`
- `podcasts/views.py` → `PodcastView` class with static methods for each version

Both endpoints accept `?limit=`, `?page=`, `?sort=asc`, and `?search=` query params. v2 adds `total_results`/`more_results` pagination metadata and a formatted `duration` field; it also strips internal DB fields (`id`, `release_date`, `duration`) from the response.

### Data Model

Single `Podcast` model (`podcasts/models.py`) with: `title`, `episode_number` (unique), `youtube_id`, `spotify_url`, `apple_music_url`, `release_date`, `preview_url`, `duration` (ms).

### Sync System

`podcasts/sync/` contains the platform clients and orchestration:

- `sync/clients/YouTube.py` — wraps Google API client, fetches recent uploads (last 30 days, up to 5 by default or all pages)
- `sync/clients/Spotify.py` — authenticates via client credentials, fetches recent or all episodes
- `sync/sync.py` — `syncYouTube()` and `syncSpotify()` orchestration functions; YouTube creates new `Podcast` records, Spotify updates existing records by matching on `release_date ± 1 day`
- `sync/helpers.py` — `log()` prints structured `[SERVICE] [TYPE] message` output

The sync is invoked via the Django management command `python manage.py sync <platform>`.

### Deployment

- CI builds and pushes a Docker image to Docker Hub on GitHub release (`jackmwhit/imp-skizz-podcast-index`)
- Runtime: Gunicorn with 4 workers (`gunicorn.conf.py`), bound to `0.0.0.0:8000`
- Static files served by WhiteNoise middleware
- Deployed via Dokploy with Traefik handling routing
