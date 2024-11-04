FROM python:3.9-slim

WORKDIR /usr/src/django-docker

COPY Pipfile Pipfile.lock ./

RUN apt-get update && \
	# Required for MySQL connections & CRON scheduler
	apt-get install -y pkg-config python3-dev default-libmysqlclient-dev build-essential cron && \
	rm -rf /var/lib/apt/lists/*

RUN pip install -U pipenv && \
	pipenv install --system

COPY jobs/crontab.txt /etc/cron.d/django_jobs
RUN chmod 0644 /etc/cron.d/django_jobs && \
    crontab /etc/cron.d/django_jobs

COPY . .
EXPOSE 8000
ENTRYPOINT [ "sh", "./entrypoint.sh" ]
