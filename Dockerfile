FROM python:3.12-slim

WORKDIR /usr/src/django-docker

COPY Pipfile Pipfile.lock ./

RUN apt-get update && \
	apt-get install -y pkg-config python3-dev default-libmysqlclient-dev build-essential && \
	rm -rf /var/lib/apt/lists/*

RUN pip install -U pipenv && \
	pipenv install --system

COPY . .
EXPOSE 8000
ENTRYPOINT [ "sh", "./entrypoint.sh" ]
