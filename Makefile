.PHONY: up down up-prod down-prod test test-be test-fe lint format

up:
	docker compose up --build

down:
	docker compose down

up-prod:
	docker compose -f docker-compose.prod.yml up --build

down-prod:
	docker compose -f docker-compose.prod.yml down

test: test-be test-fe

test-be:
	cd backend && uv run pytest

test-fe:
	cd frontend && npm test

lint:
	cd backend && uv run ruff check . && uv run mypy
	cd frontend && npm run build

format:
	cd backend && uv run ruff format .