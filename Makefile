.PHONY: help install install-dev test test-all lint format type-check security clean build docs

PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
RUFF := $(PYTHON) -m ruff
MYPY := $(PYTHON) -m mypy
BANDIT := $(PYTHON) -m bandit
TOX := $(PYTHON) -m tox

# Default target
help:
	@echo "GitHub Activity Generator - Development Commands"
	@echo "==============================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install package in production mode"
	@echo "  make install-dev    Install package with development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run tests with coverage"
	@echo "  make test-all      Run tests on all Python versions with tox"
	@echo "  make test-fast     Run tests without coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          Run linting checks (black, ruff, mypy)"
	@echo "  make format        Auto-format code with black and ruff"
	@echo "  make type-check    Run type checking with mypy"
	@echo "  make security      Run security checks with bandit"
	@echo ""
	@echo "Build & Release:"
	@echo "  make clean         Clean build artifacts"
	@echo "  make build         Build distribution packages"
	@echo "  make docs          Build documentation"
	@echo ""
	@echo "Development:"
	@echo "  make pre-commit    Install pre-commit hooks"
	@echo "  make update-deps   Update all dependencies"

install:
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e .

install-dev:
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e ".[dev]"
	@echo "✅ Development environment ready!"

test:
	$(PYTEST) tests -v --cov=src --cov-report=term-missing --cov-report=html

test-fast:
	$(PYTEST) tests -v

test-all:
	$(TOX)

lint:
	@echo "Running Black..."
	$(BLACK) --check src tests
	@echo "Running Ruff..."
	$(RUFF) check src tests
	@echo "Running MyPy..."
	$(MYPY) src tests
	@echo "✅ All linting checks passed!"

format:
	@echo "Formatting with Black..."
	$(BLACK) src tests
	@echo "Fixing with Ruff..."
	$(RUFF) check --fix src tests
	@echo "✅ Code formatted!"

type-check:
	$(MYPY) src tests

security:
	$(BANDIT) -r src
	@echo "✅ Security scan complete!"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf .tox/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	@echo "✅ Cleaned build artifacts!"

build: clean
	$(PYTHON) -m build
	@echo "✅ Build complete! Check dist/ directory"

docs:
	cd docs && make html
	@echo "✅ Documentation built! Open docs/_build/html/index.html"

pre-commit:
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "✅ Pre-commit hooks installed!"

update-deps:
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --upgrade -e ".[dev]"
	@echo "✅ Dependencies updated!"

# Run all checks before committing
check: lint type-check security test-fast
	@echo "✅ All checks passed! Ready to commit"