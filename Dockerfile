# pull official base image
FROM python:slim as builder
ARG DEBIAN_FRONTEND=noninteractive
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set environment variables
WORKDIR /pipfiles
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

# Install pipenv
RUN set -ex && pip install pipenv --upgrade

# Install dependencies
RUN set -ex && pipenv install --system --sequential --ignore-pipfile --dev

FROM builder as api
# Set work directory
WORKDIR /code

# Copy project
COPY . /code/

