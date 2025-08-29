# Makefile for Patient Appointment API

# Variables
PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip

.PHONY: venv install-dependencies install-test-dependencies test test-unit test-e2e test-e2e-with-api test-coverage run-api backup-db restore-db cleanup-db

# Create and activate virtual environment
venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created at ./$(VENV)"
	@echo "To activate: source $(VENV_BIN)/activate"

# Install project dependencies
install-dependencies: venv
	@echo "Installing project dependencies..."
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e .
	@echo "Project dependencies installed!"

# Install test dependencies
install-test-dependencies: venv
	@echo "Installing test dependencies..."
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e .[dev]
	@echo "Test dependencies installed!"

# Run all tests
test: test-unit test-e2e
	@echo "All tests completed!"

# Run unit tests
test-unit: backup-db
	@echo "Running unit tests..."
	$(VENV_BIN)/pytest tests/unit/ -v --asyncio-mode=auto
	@echo "Unit tests completed!"
	@echo "Restoring database..."
	$(VENV_BIN)/python scripts/backup_restore_db.py restore
	@echo "Database restored to original state"

# Run end-to-end tests (requires API to be running)
test-e2e: run-api backup-db
	@echo "Running end-to-end tests..."
	@echo "Warning: Make sure the API is running with 'make run-api' in another terminal"
	$(VENV_BIN)/pytest tests/e2e/ -v --asyncio-mode=auto
	@echo "E2E tests completed!"
	@echo "Restoring database..."
	$(VENV_BIN)/python scripts/backup_restore_db.py restore
	@echo "Database restored to original state"


# Run comprehensive coverage with both unit and e2e tests
coverage-full:
	@echo "Running comprehensive coverage with unit and e2e tests..."
	@echo "Clearing previous coverage data..."
	$(VENV_BIN)/python -m coverage erase
	@echo "Running unit tests with coverage..."
	$(VENV_BIN)/python -m coverage run -m pytest tests/unit/ --asyncio-mode=auto
	@echo "Backing up database for e2e tests..."
	$(VENV_BIN)/python scripts/backup_restore_db.py backup
	@echo "Starting API in background..."
	$(VENV_BIN)/python run_api.py & \
	API_PID=$$!; \
	echo "API started with PID $$API_PID"; \
	sleep 5; \
	echo "Running E2E tests with coverage (append mode)..."; \
	$(VENV_BIN)/python -m coverage run -a -m pytest tests/e2e/ --asyncio-mode=auto; \
	TEST_EXIT_CODE=$$?; \
	echo "Stopping API (PID $$API_PID)..."; \
	kill $$API_PID 2>/dev/null || true; \
	wait $$API_PID 2>/dev/null || true; \
	echo "API stopped"; \
	echo "Restoring database..."; \
	$(VENV_BIN)/python scripts/backup_restore_db.py restore; \
	echo "Cleaning up backup..."; \
	$(VENV_BIN)/python scripts/backup_restore_db.py cleanup; \
	echo "Database restored to original state"; \
	echo "Generating combined coverage report..."; \
	$(VENV_BIN)/python -m coverage report --show-missing; \
	exit $$TEST_EXIT_CODE

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	$(VENV_BIN)/pytest tests/unit/ --cov=src --cov-report=html --cov-report=term-missing -v --asyncio-mode=auto
	@echo "Coverage report generated in htmlcov/"

# Run the FastAPI application
run-api:
	@echo "Starting FastAPI application..."
	$(VENV_BIN)/python run_api.py

# Database backup and restore targets
backup-db:
	@echo "Backing up database..."
	$(VENV_BIN)/python scripts/backup_restore_db.py backup
	@echo "Database backup completed!"

restore-db:
	@echo "Restoring database from backup..."
	$(VENV_BIN)/python scripts/backup_restore_db.py restore
	@echo "Database restore completed!"

cleanup-db:
	@echo "Cleaning up database backup..."
	$(VENV_BIN)/python scripts/backup_restore_db.py cleanup
	@echo "Database backup cleanup completed!"

