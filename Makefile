.PHONY: help test test-verbose test-coverage lint format typecheck

help:
	@echo "Available commands:"
	@echo "  make test           - Run tests"
	@echo "  make test-verbose   - Run tests with verbose output"
	@echo "  make test-coverage  - Run tests with coverage"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo "  make typecheck      - Run static type checker"

test:
	PYTHONPATH=.:src uv run pytest

test-print:
	PYTHONPATH=.:src uv run pytest -s

test-verbose:
	PYTHONPATH=.:src uv run pytest -v

test-coverage:
	PYTHONPATH=.:src uv run pytest --cov --cov-report=term-missing

lint:
	PYTHONPATH=.:src uv run ruff check . --fix

format:
	PYTHONPATH=.:src uv run ruff format .

typecheck:
	PYTHONPATH=.:src uv run pyright
