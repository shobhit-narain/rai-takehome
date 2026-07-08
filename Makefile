PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
UVICORN ?= uvicorn
APP_MODULE ?= src.app.main:app
HOST ?= 127.0.0.1
PORT ?= 8000
PANDOC ?= pandoc

.PHONY: install run seed reset-db test test-unit test-integration test-api test-e2e export-docs export-trd export-implementation export-test-plan export-api-spec export-repo-blueprint lint typecheck create-deliverables

install:
	$(PIP) install -e .[dev]

run:
	$(UVICORN) $(APP_MODULE) --host $(HOST) --port $(PORT) --reload

seed:
	$(PYTHON) seed_data/scripts/seed_local_db.py

reset-db:
	$(PYTHON) seed_data/scripts/reset_local_db.py

test:
	pytest

test-unit:
	pytest tests/unit

test-integration:
	pytest tests/integration

test-api:
	pytest tests/api

test-e2e:
	pytest tests/e2e

lint:
	ruff check src tests

typecheck:
	mypy src

generate-seed-data:
	$(PYTHON) seed_data/scripts/generate_seed_data.py

reset-and-seed: reset-db generate-seed-data seed
