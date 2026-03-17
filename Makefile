.PHONY: up down dev setup test lint migrate seed plugin-check

up:
	docker compose up -d

down:
	docker compose down

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

setup:
	cp -n .env.example .env || true
	uv pip install -e ".[dev]"
	cd frontend && npm install

migrate:
	@echo "No database migrations defined yet for Phase 0."

seed:
	bash scripts/seed_data.sh

test:
	python -m pytest backend/tests -v
	cd frontend && npm run test

lint:
	ruff check backend
	mypy backend
	cd frontend && npm run lint

plugin-check:
	python backend/scripts/validate_plugins.py
