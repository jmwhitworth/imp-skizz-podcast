FROM python:3.13-slim AS pythonbuilder

# Install build dependencies for mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmariadb-dev \
    libmariadb-dev-compat \
    build-essential \
    curl \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR


# Runtime stage
FROM python:3.13-slim AS runtime

# Install runtime dependencies for mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=pythonbuilder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY . .

RUN python manage.py collectstatic --noinput --clear

EXPOSE 8000

ENTRYPOINT [ "sh", "entrypoint.sh" ]
