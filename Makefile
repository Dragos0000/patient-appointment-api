# Makefile for Patient Appointment API

# Variables
PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip

.PHONY: venv install-dependencies install-test-dependencies

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