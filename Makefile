.PHONY: help install install-web install-api dev dev-api dev-web lint lint-api lint-web format format-api format-web typecheck typecheck-api typecheck-web test test-api test-web test-e2e docker-up docker-down docker-clean docker-logs smoke eval clean

PYTHON ?= python
NPM ?= npm
DOCKER_COMPOSE ?= docker compose

help: ## Show this help menu
	@echo "======================================================================"
	@echo "Veritas — Citation-Verified Literature Review Generator"
	@echo "======================================================================"
	@echo "Usage: make <target>"
	@echo ""
	@echo "Available Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-16s %s\n", $$1, $$2}'
	@echo "======================================================================"

install: install-web install-api ## Install all dependencies (frontend and backend)

install-web: ## Install Next.js frontend dependencies
	cd apps/web && $(NPM) install

install-api: ## Install FastAPI backend dependencies
	cd apps/api && $(PYTHON) -m pip install -r requirements.txt

dev: ## Start all services via Docker Compose with build
	$(DOCKER_COMPOSE) up --build

dev-api: ## Run FastAPI backend locally with hot-reloading
	cd apps/api && $(PYTHON) -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

dev-web: ## Run Next.js frontend locally with hot-reloading
	cd apps/web && $(NPM) run dev

lint: lint-api lint-web ## Run linters and formatting checks across all workspaces

lint-api: ## Run ruff linter and formatting checks on backend
	cd apps/api && $(PYTHON) -m ruff check app tests
	cd apps/api && $(PYTHON) -m ruff format --check app tests

lint-web: ## Run eslint on frontend
	cd apps/web && $(NPM) run lint

format: format-api format-web ## Automatically format code across all workspaces

format-api: ## Format Python backend code with ruff
	cd apps/api && $(PYTHON) -m ruff format app tests
	cd apps/api && $(PYTHON) -m ruff check --fix app tests

format-web: ## Format TypeScript frontend code
	cd apps/web && $(NPM) run lint -- --fix

typecheck: typecheck-api typecheck-web ## Run static type checks across all workspaces

typecheck-api: ## Run mypy type checking on FastAPI backend
	cd apps/api && $(PYTHON) -m mypy app

typecheck-web: ## Run TypeScript type checking on Next.js frontend
	cd apps/web && npx tsc --noEmit

test: test-api test-web ## Run backend and frontend unit/integration test suites

test-api: ## Run pytest suite with test coverage report
	cd apps/api && $(PYTHON) -m pytest tests -v

test-web: ## Run frontend test suite
	cd apps/web && $(NPM) test

test-e2e: ## Run opaque-box E2E test runner
	$(PYTHON) tests/e2e/runner.py --all

docker-up: ## Start containers in detached background mode
	$(DOCKER_COMPOSE) up -d --build

docker-down: ## Stop and remove active containers and network
	$(DOCKER_COMPOSE) down

docker-clean: ## Stop containers and remove persistent volumes
	$(DOCKER_COMPOSE) down -v

docker-logs: ## Follow live logs from all running containers
	$(DOCKER_COMPOSE) logs -f

smoke: ## Execute automated end-to-end smoke test script
	$(PYTHON) scripts/smoke_test.py

eval: ## Run verification engine against ground-truth evaluation fixtures
	$(PYTHON) scripts/eval.py

clean: ## Remove build artifacts, pycache, and cache directories
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('.pytest_cache')]"
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('.mypy_cache')]"
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('.next') if p.is_dir()]"
