.PHONY: all install install-dev test lint format clean doctor check-deps help

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

help:
	@echo "RogueByte RBRT Toolkit V2 Makefile"
	@echo "=================================="
	@echo "make install       Install rbrt package"
	@echo "make install-dev   Install in editable mode with dev dependencies"
	@echo "make test          Run automated test suite"
	@echo "make lint          Run linter (ruff or internal checks)"
	@echo "make doctor        Execute rbrt doctor environment diagnosis"
	@echo "make clean         Remove build artifacts and caches"

install:
	$(PIP) install .

install-dev:
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) tests/run_tests.py

doctor:
	$(PYTHON) -m rbrt doctor

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache/ __pycache__/ src/*/__pycache__ tests/__pycache__
