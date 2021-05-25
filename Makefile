#! /usr/bin/make -f

help:
	@echo "# Makefile for 2FA"
	@echo
	@echo '### Usage:'
	@echo
	@echo '    make build	>>>	build project from docker images'
	@echo '    make up	>>>	run project in docker container'
	@echo '    make down	>>>	stop project in docker container'
	@echo '    make test	>>>	run unit tests and generate coverage report'
	@echo
	@echo '### Code style (best to run it before every commit):'
	@echo
	@echo '    make black	>>>	run black formatter'
	@echo '    make flake8	>>>	run flake8 linter'
	@echo
	@echo

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

black:
	black . --exclude="migrations/|.*_pb2.*\.py"

flake8:
	flake8

test:
	docker-compose run --rm web pytest

lock:
	pipenv lock --pre

requirements:
	pipenv lock -r > requirements.txt