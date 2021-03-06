.PHONY: help logs

help: ## This help
	@echo "Makefile for managing application:\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

pull-upstream: ## pull from upstream master
	git pull upstream master

build: ## rebuild containers
	docker-compose build

changelog:  ## create changelog since release v="version"
	python scripts/generate_changelog.py --version $(v)

up: ## start local dev environment; run migrations; populate database
	docker-compose up -d
	make migrate-up
	make populate-db

down: ## stop local dev environment
	docker-compose down

restart: ## restart local dev environment
	docker-compose restart $(args)

attach: ## attach to process for debugging purposes
	docker attach `docker-compose ps -q app`

migration: ## create migration m="message"
	docker-compose exec app flask db migrate -m "$(m)"

migration-empty: ## create empty migration m="message
	docker-compose exec app flask db revision -m "$(m)"

migrate-up: ## run all migration
	docker-compose exec app flask db upgrade

migrate-down: ## roll back last migration
	docker-compose exec app flask db downgrade

dropdb:  ## drop all tables in development database
	psql -d postgresql://bbdev_user:bbdev_password@localhost:9432/busy-beaver -f ./scripts/database/drop_all_tables.sql

populate-db:  ## populate database
	docker-compose exec app python scripts/dev/populate_database.py

requirements: ## generate requirements.txt using piptools
	pip-compile --output-file=requirements.txt requirements.in

test: ## run tests
	docker-compose exec app pytest $(args)

test-cov: ## run tests with coverage.py
	docker-compose exec app pytest --cov ./busy_beaver $(args)

test-covhtml: ## run tests and load html coverage report
	docker-compose exec app pytest --cov ./busy_beaver --cov-report html && open ./htmlcov/index.html

test-pdb:
	docker-compose exec app pytest --pdb -s

test-skipvcr: ## run non-vcr tests
	docker-compose exec app pytest -m 'not vcr'

lint: ## run flake8 linter
	docker-compose exec app flake8

logs: ## attach to logs
	docker-compose logs

debug: ## attach to app container for debugging
	docker attach `docker-compose ps -q app`

shell: ## log into into app container -- bash-shell
	docker-compose exec app bash

shell-db:  ## log into database container -- psql
	docker-compose exec db psql -w --username "bbdev_user" --dbname "busy-beaver"

devshell:  ## open ipython shell with application context
	docker-compose exec app ipython -i scripts/dev/shell.py

flaskcli:  ## use flask cli to run commands args='args'te
	docker-compose exec app flask $(args)

ngrok: ## start ngrok to forward port
	ngrok http 5000

prod-build-image:
	docker build -f docker/prod/Dockerfile --tag alysivji/busy-beaver .

prod-build: ## build production images
	docker-compose -f docker-compose.prod.yml build

prod-migrate-up:
	docker-compose -f docker-compose.prod.yml exec app flask db upgrade

prod-migrate-down:
	docker-compose -f docker-compose.prod.yml exec app flask db downgrade

prod-up: ## start prod environment
	docker-compose -f docker-compose.prod.yml up -d
	make prod-migrate-up

prod-down: ## stop prod environment
	docker-compose -f docker-compose.prod.yml down

prod-pull-image: ## pull latest deployment image
	docker pull alysivji/busy-beaver:latest

prod-deploy: prod-pull-image ## redeploy application
	make prod-down
	make prod-up

prod-shell:  ## shell into production container
	docker-compose -f docker-compose.prod.yml exec app bash

prod-shell-db:  ## shell into prodution postgres instance
	psql -d "${DATABASE_URI}"

prod-logs: ## attach to logs in production container
	docker-compose -f docker-compose.prod.yml logs
