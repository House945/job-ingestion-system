.PHONY: up down test test-be test-fe lint

up:
	docker compose up --build

down:
	docker compose down

test: test-be test-fe

test-be:
	cd backend && uv run pytest

test-fe:
	cd frontend && npm test

lint:
	cd backend && uv run ruff check . && uv run mypy
	cd frontend && npm run build