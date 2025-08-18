.PHONY: help install dev test lint format clean docker-up docker-down docker-build

help: ## Show this help message
	@echo "Link Ingestor - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -e .

dev: ## Start development server
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html

lint: ## Run linting
	ruff check .
	mypy app/

format: ## Format code
	black .
	ruff check --fix .

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov

docker-up: ## Start all services with Docker Compose
	docker-compose up -d

docker-down: ## Stop all services
	docker-compose down

docker-build: ## Build Docker images
	docker-compose build

docker-logs: ## View logs from all services
	docker-compose logs -f

docker-logs-api: ## View API service logs
	docker-compose logs -f api

docker-logs-worker: ## View worker service logs
	docker-compose logs -f worker

docker-shell: ## Open shell in API container
	docker-compose exec api bash

docker-db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U linkuser -d link_ingestor

docker-redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

setup-dev: ## Setup development environment
	pip install -e .
	cp env.example .env
	@echo "Development environment setup complete!"
	@echo "Please edit .env file with your configuration"

run-system-test: ## Run the system test script
	python test_system.py

check-health: ## Check system health
	@echo "Checking system health..."
	@curl -s http://localhost:8000/health || echo "API not responding"
	@echo "PostgreSQL: $(shell docker-compose exec -T postgres pg_isready -U linkuser -d link_ingestor > /dev/null 2>&1 && echo "OK" || echo "Not responding")"
	@echo "Redis: $(shell docker-compose exec -T redis redis-cli ping > /dev/null 2>&1 && echo "OK" || echo "Not responding")"

monitor: ## Open monitoring dashboards
	@echo "Opening monitoring dashboards..."
	@echo "Grafana: http://localhost:3000 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"
	@echo "API Docs: http://localhost:8000/docs"

reset-db: ## Reset database (WARNING: This will delete all data)
	docker-compose exec postgres psql -U linkuser -d link_ingestor -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	@echo "Database reset complete"

backup-db: ## Create database backup
	docker-compose exec postgres pg_dump -U linkuser link_ingestor > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Database backup created"

restore-db: ## Restore database from backup (usage: make restore-db BACKUP_FILE=backup.sql)
	@if [ -z "$(BACKUP_FILE)" ]; then echo "Usage: make restore-db BACKUP_FILE=backup.sql"; exit 1; fi
	docker-compose exec -T postgres psql -U linkuser -d link_ingestor < $(BACKUP_FILE)
	@echo "Database restored from $(BACKUP_FILE)"



