# Setup Guide

## 1. Purpose

This guide explains how to configure the local environment and run the API service, scripts, and test suite for the Time-Off Microservice on Linux using bash.

## 2. Prerequisites

Install the following before setup:

- Python 3.11 or newer
- `pip`
- `make`
- Pandoc if document export is needed

Optional but recommended:

- `venv` support
- a PDF engine supported by Pandoc for PDF export

## 3. Clone and Enter the Repository

```bash
git clone <repository-url>
cd timeoff-microservice
```

## 4. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 5. Install Dependencies

### Option A: Install from `pyproject.toml`

Install runtime and development dependencies:

```bash
pip install -e .[dev]
```

Install runtime dependencies only:

```bash
pip install -e .
```

### Option B: Install from `requirements.txt`

```bash
pip install -r requirements.txt
```

## 6. Configure Environment Variables

Copy the example file:

```bash
cp .env.example .env
```

Export variables into the shell:

```bash
export APP_ENV=local
export SQLITE_URL=sqlite:///./local.db
export DEFAULT_HCM_PROVIDER=mock_hcm
export ENABLE_RESPONSE_CACHE=false
export LOG_LEVEL=INFO
export API_HOST=127.0.0.1
export API_PORT=8000
```

If your application loads environment variables from `.env`, update the file values there as needed.

## 7. Initialize or Seed Local Data

Seed the local SQLite database:

```bash
make seed
```

If you are not using `make`, run:

```bash
python scripts/seed_local_db.py
```

Reset the local database:

```bash
make reset-db
```

Or:

```bash
python scripts/reset_local_db.py
```

## 8. Run the API Service

### Using Make

```bash
make run
```

### Using uvicorn directly

```bash
uvicorn src.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Expected base URL

```text
http://127.0.0.1:8000
```

### Example health check

```bash
curl http://127.0.0.1:8000/api/v1/health
```

## 9. Run Scripts

The project supports running internal scripts through the API and through Python services.

### Run through API

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/scripts/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-token>" \
  -d '{
    "name": "sync_all_balances",
    "params": {
      "location_id": "loc_us_ca"
    }
  }'
```

### Schedule through API

```bash
curl -X POST http://127.0.0.1:8000/api/v1/scripts/schedule \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-token>" \
  -d '{
    "name": "reconcile_recent_leaves",
    "cron_expression": "0 */6 * * *",
    "params": {}
  }'
```

### Query script status

```bash
curl http://127.0.0.1:8000/api/v1/scripts/<run_id>/status \
  -H "Authorization: Bearer <admin-token>"
```

### Cancel a script run

```bash
curl -X POST http://127.0.0.1:8000/api/v1/scripts/<run_id>/cancel \
  -H "Authorization: Bearer <admin-token>"
```

## 10. Run Tests

### Run all tests

```bash
make test
```

Or:

```bash
pytest
```

### Run unit tests

```bash
make test-unit
```

Or:

```bash
pytest tests/unit
```

### Run integration tests

```bash
make test-integration
```

Or:

```bash
pytest tests/integration
```

### Run API tests

```bash
make test-api
```

Or:

```bash
pytest tests/api
```

### Run end-to-end tests

```bash
make test-e2e
```

Or:

```bash
pytest tests/e2e
```

### Run a single test file

```bash
pytest tests/e2e/test_manager_approval_flow.py
```

### Run a single test case

```bash
pytest tests/e2e/test_manager_approval_flow.py::test_manager_approval_flow
```

## 11. Run Quality Checks

### Run lint

```bash
make lint
```

Or:

```bash
ruff check src tests
```

### Run type checking

```bash
make typecheck
```

Or:

```bash
mypy src
```

## 12. Export Documents

Export all main documents:

```bash
make export-docs
```

Export only the TRD:

```bash
make export-trd
```

Direct Pandoc example:

```bash
pandoc docs/TRD.md -o deliverables/TRD.pdf
```

## 13. Suggested Development Workflow

1. create and activate the virtual environment
2. install dependencies
3. copy `.env.example` to `.env`
4. export environment variables if needed
5. reset or seed the database
6. run the API locally
7. run unit tests
8. run integration and API tests
9. run end-to-end tests before final review
10. export documents for submission

## 14. Troubleshooting

### Import errors when running the app

Make sure the virtual environment is active and dependencies are installed.

### SQLite file not found

Verify `SQLITE_URL` and ensure the seed or reset step has been run.

### Tests fail due to stale DB state

Reset the database and rerun seed or setup steps.

### `make` command not found

Run the equivalent Python or pytest commands directly.

### Pandoc export fails

Confirm Pandoc is installed and a supported PDF engine is available.

## 15. Recommended Commands Summary

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
make reset-db
make seed
make run
make test
make export-docs
```

## Generate deterministic seed files

```bash
python scripts/generate_seed_data.py
```

### Reset and seed local DB

```bash
python scripts/reset_local_db.py
python scripts/seed_local_db.py
```