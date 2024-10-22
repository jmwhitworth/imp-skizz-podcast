# Stage 1: Use NPM to run build command
FROM node:21 AS node-build

WORKDIR /app

COPY package*.json ./
RUN npm install
COPY . .

RUN npm run build

# Stage 2: Use Python for running the app, and take output files from Stage 1
FROM python:3.9-slim

WORKDIR /usr/src/django-docker

COPY Pipfile Pipfile.lock ./

RUN apt-get update && \
	# Required for MySQL connections
	apt-get install -y pkg-config python3-dev default-libmysqlclient-dev build-essential && \
	rm -rf /var/lib/apt/lists/*

RUN pip install -U pipenv && \
	pipenv install --system

COPY --from=node-build /app .
EXPOSE 8000
ENTRYPOINT [ "sh", "./entrypoint.sh" ]
