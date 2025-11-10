.PHONY: help install install-dev test test-cov lint format clean build pre-commit

# Default target
help:
	@echo "YouTube Downloader - Development Commands"
	@echo "=========================================="
	@echo ""
	@echo "Installation:"
	@echo "  make install          Install package in development mode"
	@echo "  make install-dev      Install with development dependencies"
	@echo ""
	@echo "Testing & Coverage:"
	@echo "  make test             Run pytest"
	@echo "  make test-cov         Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run all linters (flake8, black, isort, mypy)"
	@echo "  make format           Auto-format code (black, isort)"
	@echo ""
	@echo "Build & Distribution:"
	@echo "  make build            Build distribution packages"
	@echo "  make clean            Remove build artifacts and cache files"
	@echo ""
	@echo "Pre-commit:"
	@echo "  make pre-commit       Install pre-commit hooks"
	@echo ""
	@echo "Utilities:"
	@echo "  make help             Show this help message"
	@echo ""

# Installation targets
install:
	@echo "Installing youtube-downloader in development mode..."
	pip install -e .

install-dev:
	@echo "Installing youtube-downloader with development dependencies..."
	pip install -e ".[dev]"

# Testing targets
test:
	@echo "Running pytest..."
	pytest

test-cov:
	@echo "Running pytest with coverage..."
	pytest --cov=youtube_downloader --cov-report=html --cov-report=term-missing

# Linting targets
lint:
	@echo "Running linters..."
	@echo "  - flake8"
	flake8 youtube_downloader tests
	@echo "  - black (check)"
	black --check youtube_downloader tests
	@echo "  - isort (check)"
	isort --check-only youtube_downloader tests
	@echo "  - mypy"
	mypy youtube_downloader

# Formatting targets
format:
	@echo "Auto-formatting code..."
	@echo "  - black"
	black youtube_downloader tests
	@echo "  - isort"
	isort youtube_downloader tests
	@echo "Code formatting complete!"

# Build targets
clean:
	@echo "Cleaning build artifacts and cache files..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -delete
	@echo "Clean complete!"

build: clean
	@echo "Building distribution packages..."
	python -m build
	@echo "Build complete! Packages available in dist/"

# Pre-commit hooks
pre-commit:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Pre-commit hooks installed!"

# Additional convenience targets
.PHONY: check
check: lint test
	@echo "All checks passed!"

.PHONY: dev-setup
dev-setup: install-dev pre-commit
	@echo "Development environment setup complete!"
