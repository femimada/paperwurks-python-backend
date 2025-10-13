# Paperwurks Backend Makefile
# Simplifies common development tasks

.PHONY: help
.DEFAULT_GOAL := help

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Docker Compose files (must chain base + environment specific)
COMPOSE_BASE := docker-compose.yml
COMPOSE_DEV := $(COMPOSE_BASE) -f docker-compose.dev.yml
COMPOSE_TEST := $(COMPOSE_BASE) -f docker-compose.test.yml

##@ General

help: ## Display this help message
	@echo "$(BLUE)Paperwurks Backend - Development Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

up: ## Start all services (backend, worker, postgres, redis, localstack)
	@echo "$(GREEN)Starting development environment...$(NC)"
	docker-compose -f $(COMPOSE_DEV) up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "  Backend: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/api/docs"
	@echo "  Admin: http://localhost:8000/admin"

down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker-compose -f $(COMPOSE_DEV) down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: down up ## Restart all services

logs: ## Follow logs for all services
	docker-compose -f $(COMPOSE_DEV) logs -f

logs-backend: ## Follow backend logs only
	docker-compose -f $(COMPOSE_DEV) logs -f backend

logs-worker: ## Follow worker logs only
	docker-compose -f $(COMPOSE_DEV) logs -f worker

build: ## Rebuild Docker images
	@echo "$(YELLOW)Rebuilding Docker images...$(NC)"
	docker-compose -f $(COMPOSE_DEV) build
	@echo "$(GREEN)✓ Images rebuilt$(NC)"

rebuild: down build up ## Rebuild and restart all services

ps: ## Show running containers
	docker-compose -f $(COMPOSE_DEV) ps

##@ Database

migrate: ## Run database migrations
	@echo "$(YELLOW)Running migrations...$(NC)"
	docker-compose -f $(COMPOSE_DEV) exec backend python manage.py migrate
	@echo "$(GREEN)✓ Migrations complete$(NC)"

makemigrations: ## Create new migrations
	@echo "$(YELLOW)Creating migrations...$(NC)"
	docker-compose -f $(COMPOSE_DEV) exec backend python manage.py makemigrations
	@echo "$(GREEN)✓ Migrations created$(NC)"

migrations-status: ## Show migration status
	docker-compose -f $(COMPOSE_DEV) exec backend python manage.py showmigrations

db-shell: ## Open database shell (psql)
	docker-compose -f $(COMPOSE_DEV) exec postgres psql -U postgres -d paperwurks_dev

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)WARNING: This will destroy all database data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(YELLOW)Resetting database...$(NC)"; \
		docker-compose -f $(COMPOSE_DEV) down -v; \
		docker-compose -f $(COMPOSE_DEV) up -d postgres redis localstack; \
		sleep 5; \
		docker-compose -f $(COMPOSE_DEV) up -d backend worker; \
		sleep 3; \
		make migrate; \
		echo "$(GREEN)✓ Database reset complete$(NC)"; \
	fi

##@ Django Management

shell: ## Open Django shell
	docker-compose -f $(COMPOSE_DEV) exec backend python manage.py shell

superuser: ## Create Django superuser
	docker-compose -f $(COMPOSE_DEV) exec backend python manage.py createsuperuser

collectstatic: ## Collect static files
	docker-compose -f $(COMPOSE_DEV) exec backend python manage.py collectstatic --noinput

##@ Testing

test: ## Run all tests
	@echo "$(YELLOW)Running tests...$(NC)"
	docker-compose -f $(COMPOSE_DEV) exec backend pytest
	@echo "$(GREEN)✓ Tests complete$(NC)"

test-coverage: ## Run tests with coverage report
	@echo "$(YELLOW)Running tests with coverage...$(NC)"
	docker-compose -f $(COMPOSE_DEV) exec backend pytest --cov=apps --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

test-verbose: ## Run tests with verbose output
	docker-compose -f $(COMPOSE_DEV) exec backend pytest -v

test-file: ## Run specific test file (usage: make test-file FILE=apps/users/tests/test_models.py)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: FILE parameter required$(NC)"; \
		echo "Usage: make test-file FILE=apps/users/tests/test_models.py"; \
		exit 1; \
	fi
	docker-compose -f $(COMPOSE_DEV) exec backend pytest $(FILE)

lint: ## Run code linting (flake8, black)
	@echo "$(YELLOW)Running linters...$(NC)"
	docker-compose -f $(COMPOSE_DEV) exec backend black --check apps/
	docker-compose -f $(COMPOSE_DEV) exec backend flake8 apps/

format: ## Auto-format code with black
	@echo "$(YELLOW)Formatting code...$(NC)"
	docker-compose -f $(COMPOSE_DEV) exec backend black apps/
	@echo "$(GREEN)✓ Code formatted$(NC)"

##@ Celery

celery-status: ## Check Celery worker status
	docker-compose -f $(COMPOSE_DEV) exec worker celery -A apps.config inspect ping

celery-active: ## Show active Celery tasks
	docker-compose -f $(COMPOSE_DEV) exec worker celery -A apps.config inspect active

celery-registered: ## Show registered Celery tasks
	docker-compose -f $(COMPOSE_DEV) exec worker celery -A apps.config inspect registered

celery-purge: ## Purge all Celery tasks (development only)
	@echo "$(RED)WARNING: This will purge all pending tasks!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose -f $(COMPOSE_DEV) exec worker celery -A apps.config purge; \
	fi

##@ Health Checks

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo ""
	@echo "$(YELLOW)Backend:$(NC)"
	@curl -s http://localhost:8000/api/health | jq . || echo "$(RED)✗ Backend not responding$(NC)"
	@echo ""
	@echo "$(YELLOW)Postgres:$(NC)"
	@docker-compose -f $(COMPOSE_DEV) exec postgres pg_isready -U postgres || echo "$(RED)✗ Postgres not ready$(NC)"
	@echo ""
	@echo "$(YELLOW)Redis:$(NC)"
	@docker-compose -f $(COMPOSE_DEV) exec redis redis-cli --no-auth-warning -a devpassword ping || echo "$(RED)✗ Redis not responding$(NC)"
	@echo ""
	@echo "$(YELLOW)Celery Worker:$(NC)"
	@docker-compose -f $(COMPOSE_DEV) exec worker celery -A apps.config inspect ping || echo "$(RED)✗ Worker not responding$(NC)"

##@ Cleanup

clean: ## Remove all containers, volumes, and orphaned containers
	@echo "$(YELLOW)Cleaning up...$(NC)"
	docker-compose -f $(COMPOSE_DEV) down -v --remove-orphans
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-images: ## Remove backend Docker images
	@echo "$(YELLOW)Removing backend images...$(NC)"
	docker-compose -f $(COMPOSE_DEV) down --rmi local
	@echo "$(GREEN)✓ Images removed$(NC)"

prune: ## Remove all unused Docker resources (WARNING: affects all Docker containers)
	@echo "$(RED)WARNING: This will remove all unused Docker containers, networks, and volumes!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker system prune -af --volumes; \
		echo "$(GREEN)✓ Docker system pruned$(NC)"; \
	fi

##@ Production

build-prod: ## Build production Docker image
	@echo "$(YELLOW)Building production image...$(NC)"
	docker build --target production -t paperwurks-backend:latest .
	@echo "$(GREEN)✓ Production image built$(NC)"

build-worker: ## Build worker Docker image
	@echo "$(YELLOW)Building worker image...$(NC)"
	docker build --target worker -t paperwurks-worker:latest .
	@echo "$(GREEN)✓ Worker image built$(NC)"

test-prod: ## Test production image locally
	@echo "$(YELLOW)Starting production image...$(NC)"
	docker run -p 8000:8000 --env-file .env.prod paperwurks-backend:latest

##@ Dependencies

requirements: ## Update requirements files
	@echo "$(YELLOW)Compiling requirements...$(NC)"
	docker-compose -f $(COMPOSE_DEV) run --rm backend pip-compile requirements/base.in -o requirements/base.txt
	docker-compose -f $(COMPOSE_DEV) run --rm backend pip-compile requirements/dev.in -o requirements/dev.txt
	docker-compose -f $(COMPOSE_DEV) run --rm backend pip-compile requirements/prod.in -o requirements/prod.txt
	@echo "$(GREEN)✓ Requirements compiled$(NC)"

pip-install: ## Install Python dependencies
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	docker-compose -f $(COMPOSE_DEV) exec backend pip install -r requirements/base.txt -r requirements/dev.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

##@ Quick Commands

dev: up migrate ## Start development environment and run migrations
	@echo "$(GREEN)✓ Development environment ready!$(NC)"

fresh: clean up migrate superuser ## Fresh start with new database and superuser
	@echo "$(GREEN)✓ Fresh environment ready!$(NC)"

check: lint test ## Run linting and tests
	@echo "$(GREEN)✓ All checks passed!$(NC)"