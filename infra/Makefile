.PHONY: up down build migrate makemigrations createsuperuser shell test init

up:
	docker compose -f docker-compose.yml up -d

down:
	docker compose -f docker-compose.yml down

build:
	docker compose -f docker-compose.yml build

migrate:
	docker compose -f docker-compose.yml exec backend python manage.py migrate

makemigrations:
	docker compose -f docker-compose.yml exec backend python manage.py makemigrations

createsuperuser:
	docker compose -f docker-compose.yml exec backend python manage.py createsuperuser

shell:
	docker compose -f docker-compose.yml exec backend python manage.py shell

test:
	docker compose -f docker-compose.yml exec backend pytest

init: build up migrate
