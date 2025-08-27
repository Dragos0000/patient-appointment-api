# Makefile for Patient Appointment API

# Variables
PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip

.PHONY: venv install-dependencies install-test-dependencies test test-unit test-coverage

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
test: test-unit
	@echo "All tests completed!"

# Run unit tests
test-unit:
	@echo "Running unit tests..."
	$(VENV_BIN)/pytest tests/unit/ -v --asyncio-mode=auto
	@echo "Unit tests completed!"

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	$(VENV_BIN)/pytest tests/unit/ --cov=src --cov-report=html --cov-report=term-missing -v --asyncio-mode=auto
	@echo "Coverage report generated in htmlcov/"



