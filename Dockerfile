# pull official base image
FROM python:3.9.0

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN set -ex && pip install pipenv --upgrade
RUN set -ex && mkdir -p /code
# Set work directory
WORKDIR /code

# Copy project
COPY . /code/

# Install dependencies
RUN set -ex && pipenv install --deploy --system
