<#
.SYNOPSIS
    Veritas Developer Automation Script (PowerShell)
.DESCRIPTION
    Provides native command execution mirroring the root Makefile targets.
.EXAMPLE
    .\scripts\run.ps1 install
    .\scripts\run.ps1 dev
    .\scripts\run.ps1 test
    .\scripts\run.ps1 smoke
#>

param(
    [Parameter(Position=0, Mandatory=$false)]
    [ValidateSet("help", "install", "dev", "dev-api", "dev-web", "lint", "format", "typecheck", "test", "test-api", "test-web", "test-e2e", "docker-up", "docker-down", "docker-clean", "docker-logs", "smoke", "eval", "clean")]
    [string]$Command = "help"
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host "Veritas — Developer PowerShell Automation" -ForegroundColor Cyan
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host "Usage: .\scripts\run.ps1 <command>`n"
    Write-Host "Commands:"
    Write-Host "  install      Install all frontend and backend dependencies"
    Write-Host "  dev          Start stack using Docker Compose"
    Write-Host "  dev-api      Run FastAPI backend locally with hot reload"
    Write-Host "  dev-web      Run Next.js frontend locally with hot reload"
    Write-Host "  lint         Run ruff and eslint checks"
    Write-Host "  format       Auto-format codebase with ruff and eslint"
    Write-Host "  typecheck    Run mypy and tsc --noEmit"
    Write-Host "  test         Run backend pytest and frontend vitest"
    Write-Host "  test-api     Run backend pytest"
    Write-Host "  test-web     Run frontend vitest"
    Write-Host "  test-e2e     Run E2E opaque-box test runner"
    Write-Host "  docker-up    Start Docker containers in background"
    Write-Host "  docker-down  Stop Docker containers"
    Write-Host "  docker-clean Stop containers and destroy volumes"
    Write-Host "  docker-logs  Tail container logs"
    Write-Host "  smoke        Run smoke test script"
    Write-Host "  eval         Run 10-pair evaluation fixture benchmark"
    Write-Host "  clean        Clean caches and build artifacts"
    Write-Host "======================================================================" -ForegroundColor Cyan
}

switch ($Command) {
    "help" { Show-Help }
    "install" {
        Write-Host "Installing frontend dependencies..." -ForegroundColor Green
        Set-Location apps/web; npm install; Set-Location ../..
        Write-Host "Installing backend dependencies..." -ForegroundColor Green
        Set-Location apps/api; python -m pip install -r requirements.txt; Set-Location ../..
    }
    "dev" {
        docker compose up --build
    }
    "dev-api" {
        Set-Location apps/api; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000; Set-Location ../..
    }
    "dev-web" {
        Set-Location apps/web; npm run dev; Set-Location ../..
    }
    "lint" {
        Write-Host "Running backend lint checks..." -ForegroundColor Green
        Set-Location apps/api; python -m ruff check app tests; python -m ruff format --check app tests; Set-Location ../..
        Write-Host "Running frontend lint checks..." -ForegroundColor Green
        Set-Location apps/web; npm run lint; Set-Location ../..
    }
    "format" {
        Write-Host "Formatting backend..." -ForegroundColor Green
        Set-Location apps/api; python -m ruff format app tests; python -m ruff check --fix app tests; Set-Location ../..
        Write-Host "Formatting frontend..." -ForegroundColor Green
        Set-Location apps/web; npm run lint -- --fix; Set-Location ../..
    }
    "typecheck" {
        Write-Host "Running backend type check (mypy)..." -ForegroundColor Green
        Set-Location apps/api; python -m mypy app; Set-Location ../..
        Write-Host "Running frontend type check (tsc)..." -ForegroundColor Green
        Set-Location apps/web; npx tsc --noEmit; Set-Location ../..
    }
    "test" {
        Write-Host "Running backend tests..." -ForegroundColor Green
        Set-Location apps/api; python -m pytest tests -v; Set-Location ../..
        Write-Host "Running frontend tests..." -ForegroundColor Green
        Set-Location apps/web; npm test; Set-Location ../..
    }
    "test-api" {
        Set-Location apps/api; python -m pytest tests -v; Set-Location ../..
    }
    "test-web" {
        Set-Location apps/web; npm test; Set-Location ../..
    }
    "test-e2e" {
        python tests/e2e/runner.py --all
    }
    "docker-up" {
        docker compose up -d --build
    }
    "docker-down" {
        docker compose down
    }
    "docker-clean" {
        docker compose down -v
    }
    "docker-logs" {
        docker compose logs -f
    }
    "smoke" {
        python scripts/smoke_test.py
    }
    "eval" {
        Set-Location apps/api; python -m app.services.verification --eval; Set-Location ../..
    }
    "clean" {
        Write-Host "Cleaning caches..." -ForegroundColor Yellow
        Get-ChildItem -Path . -Include __pycache__, .pytest_cache, .mypy_cache, .next -Recurse -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
        Write-Host "Clean complete." -ForegroundColor Green
    }
}
