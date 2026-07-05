# Time-Off Microservice

## Overview

Time-Off Microservice is a Python backend service for managing employee leave requests and leave balances.

The service supports:

- employee self-service leave workflows
- manager approval and denial workflows
- local balance storage in SQLite
- synchronization with an external HCM through a canonical adapter
- mock HCM endpoints for simulation and tests
- scheduled reconciliation and backfill scripts
- a layered automated test suite

## Primary Stack

- Python
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- httpx
- APScheduler
- pytest

## Repository Documents

- `docs/TRD.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/TEST_PLAN.md`
- `docs/API_SPEC.md`
- `docs/REPO_BLUEPRINT.md`
- `docs/EXPORT.md`

## Repository Layout

```text
src/
  app/
  api/
  auth/
  domain/
  services/
  repositories/
  adapters/
  infra/

tests/
  unit/
  integration/
  api/
  e2e/

docs/
scripts/
```

## Core Capabilities

- authenticated leave balance lookup
- leave request creation
- leave request update actions
- manager leave queue
- canonical HCM adapter flow
- resilient upstream HTTP calls
- in-memory caching and rate-limit coordination
- scheduled balance sync and reconciliation
- mock HCM scenario simulation

## Local Development

### Prerequisites

Install the following:

- Python 3.11 or newer
- `make`
- Pandoc for document export
- a PDF engine supported by Pandoc if PDF export is needed

### Setup

```bash
make install
```

### Run the service

```bash
make run
```

### Seed local data

```bash
make seed
```

### Reset local database

```bash
make reset-db
```

## Testing

Run the full test suite:

```bash
make test
```

Run only unit tests:

```bash
make test-unit
```

Run only integration tests:

```bash
make test-integration
```

Run only API tests:

```bash
make test-api
```

Run only end-to-end tests:

```bash
make test-e2e
```

## Documentation Export

Export the main documents:

```bash
make export-docs
```

Export only the TRD PDF:

```bash
make export-trd
```

See `docs/EXPORT.md` for detailed export instructions.

## Suggested Environment Variables

```text
APP_ENV=local
SQLITE_URL=sqlite:///./local.db
DEFAULT_HCM_PROVIDER=mock_hcm
ENABLE_RESPONSE_CACHE=false
LOG_LEVEL=INFO
```

## Suggested Make Targets

```bash
make install
make run
make seed
make reset-db
make test
make test-unit
make test-integration
make test-api
make test-e2e
make export-docs
```

## API Summary

Base path:

```text
/api/v1
```

Main route groups:

- `/api/v1/leaves`
- `/api/v1/scripts`
- `/api/v1/mock-hcm`

See `docs/API_SPEC.md` for full request and response details.

## Notes

- SQLite is used for local persistence and testability.
- HCM remains the external source of truth for balance data.
- Mock HCM routes exist to support scenario-driven tests and local development.
- The codebase is organized as a modular monolith for simplicity and strong test coverage.