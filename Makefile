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
	$(PYTHON) scripts/seed_local_db.py

reset-db:
	$(PYTHON) scripts/reset_local_db.py

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

create-deliverables:
	mkdir -p deliverables

generate-seed-data:
	$(PYTHON) scripts/generate_seed_data.py

reset-and-seed: reset-db generate-seed-data seed

export-docs: create-deliverables export-trd export-implementation export-test-plan export-api-spec export-repo-blueprint

export-trd:
	$(PANDOC) -s -V geometry:margin=1in docs/TRD.md -o deliverables/TRD.pdf

export-implementation:
	$(PANDOC) -s -V geometry:margin=1in docs/IMPLEMENTATION_PLAN.md -o deliverables/IMPLEMENTATION_PLAN.pdf

export-test-plan:
	$(PANDOC) -s -V geometry:margin=1in docs/TEST_PLAN.md -o deliverables/TEST_PLAN.pdf

export-api-spec:
	$(PANDOC) -s -V geometry:margin=1in docs/API_SPEC.md -o deliverables/API_SPEC.pdf

export-repo-blueprint:
	$(PANDOC) -s -V geometry:margin=1in docs/REPO_BLUEPRINT.md -o deliverables/REPO_BLUEPRINT.pdf