# Time-Off Microservice Implementation Plan

## 1. Purpose

This document defines a cost-efficient implementation plan for the Python Time-Off Microservice.

The plan is optimized for:

- minimal agent count
- low context switching
- clear ownership boundaries
- high testability
- incremental delivery

## 2. Delivery Strategy

The project will be implemented by three agents:

- Agent 1: foundation and infrastructure
- Agent 2: domain and application logic
- Agent 3: API and test harness

This split keeps each agent focused on a coherent slice of the system while reducing coordination overhead.

## 3. Shared Rules

All agents must follow these rules:

- keep files small and single-purpose
- do not duplicate domain logic across layers
- prefer constructor injection or explicit dependency providers
- write tests with each feature
- use deterministic fixtures
- preserve stable interfaces once a module is published
- avoid speculative abstractions beyond the documented design

## 4. Phase Plan

### Phase 1: Foundation and Data Layer

Owner: Agent 1

Tasks:

1. create project scaffold
2. configure dependency management
3. create application bootstrap
4. add config management
5. add request ID middleware
6. add shared exceptions
7. create SQLAlchemy base, engine, and session handling
8. define ORM models
9. implement schema initialization
10. implement deterministic seed service
11. create repository classes
12. add repository integration tests
13. implement in-memory cache backend
14. implement rate-limit state models
15. implement HTTP wrapper, retry policy, and upstream error classes
16. implement scheduler wrapper and script registry base

Outputs:

- app bootstrap works
- database initializes cleanly
- seed flow works
- repositories are operational
- HTTP wrapper and cache layer exist
- scheduler infrastructure exists

Exit criteria:

- local app starts
- test database works
- repository tests pass
- infrastructure unit tests pass

### Phase 2: Domain, Services, and HCM Integration

Owner: Agent 2

Tasks:

1. define domain enums and domain errors
2. implement `LoggedInUser`
3. implement leave state machine
4. implement leave policy service
5. define domain models and commands
6. implement users service
7. implement balances service
8. implement audit service
9. implement leaves service
10. implement reconciliation service
11. define canonical HCM protocol
12. define canonical HCM models
13. implement HCM mapper
14. implement mock HCM adapter
15. add provider adapter stubs
16. implement built-in scripts:
   - `sync_all_balances`
   - `reconcile_recent_leaves`
   - `backfill_balances`
   - `repair_pending_reconciliation`
17. add domain and service unit tests
18. add service integration tests

Outputs:

- core leave workflows exist
- HCM adapter path exists
- reconciliation logic exists
- script logic exists

Exit criteria:

- employee request flow works through services
- manager approval flow works through services
- pending reconciliation flow works
- domain and service tests pass

### Phase 3: API, Auth Wiring, and Full Test Harness

Owner: Agent 3

Tasks:

1. implement auth dependencies
2. implement token resolver
3. implement shared dependency providers
4. implement request and response schemas
5. implement health routes
6. implement leaves routes
7. implement scripts routes
8. implement mock HCM routes
9. implement exception handlers and error envelopes
10. add FastAPI route metadata
11. create pytest app factory
12. create dependency override helpers
13. create auth helpers
14. create mock HCM test helpers
15. create API tests
16. create end-to-end tests
17. add CI configuration
18. add docs export instructions

Outputs:

- full HTTP API exists
- auth and authorization are enforced
- API and end-to-end tests exist
- docs and CI are ready

Exit criteria:

- protected routes enforce role rules
- API tests pass
- end-to-end tests pass
- coverage thresholds pass

## 5. Agent Responsibilities

### Agent 1: Foundation and Infrastructure

Owns:

- project structure
- app bootstrap
- config
- middleware
- shared exceptions
- database session and models
- seeds
- repositories
- cache
- HTTP client
- retry policy
- upstream error classes
- scheduler base
- script registry base

Must not own:

- leave business rules
- route handlers
- authorization policy decisions beyond shared plumbing

### Agent 2: Domain and Application Logic

Owns:

- current-user model
- enums
- domain errors
- leave state machine
- leave policy
- domain command models
- application services
- reconciliation logic
- audit logic
- HCM protocol
- HCM adapter models
- mock HCM adapter
- built-in script implementations

Must not own:

- ORM model definitions
- route handler code
- FastAPI dependency wiring

### Agent 3: API and Test Harness

Owns:

- auth dependencies
- token resolution
- shared dependency providers
- request and response schemas
- all routers
- exception-to-response mapping
- API route metadata
- pytest app factory
- dependency overrides
- API tests
- end-to-end tests
- CI and docs export flow

Must not own:

- domain rule duplication
- direct SQL queries outside test setup

## 6. Handoff Contracts

### Agent 1 to Agent 2

Agent 1 must publish stable interfaces for:

- DB session access
- repository class constructors and methods
- cache interface
- HTTP client interface
- rate-limit interface
- scheduler base and script registry base

### Agent 2 to Agent 3

Agent 2 must publish stable interfaces for:

- auth-facing current-user model
- services constructors and public methods
- canonical HCM protocol
- domain command models
- script names and parameter shapes

### Agent 1 and Agent 2 to Agent 3

Both must avoid breaking public method names once API work begins.

## 7. Work Sequence

Recommended execution order:

1. Agent 1 completes project scaffold, DB, repositories, cache, HTTP client, scheduler base
2. Agent 2 starts once repository and infrastructure interfaces are stable
3. Agent 3 starts once service interfaces and schema shapes are mostly stable
4. Agent 3 finishes with API tests and end-to-end tests
5. All agents support bug-fix pass only after main implementation is complete

## 8. Acceptance Gates

### Gate 1: Foundation Complete

Required:

- app starts
- database initializes
- seed flow works
- repositories pass tests
- HTTP wrapper tests pass
- cache tests pass

### Gate 2: Domain Complete

Required:

- leave state machine implemented
- leave policy implemented
- leaves service implemented
- reconciliation service implemented
- mock HCM adapter implemented
- service tests pass

### Gate 3: API Complete

Required:

- health, leaves, scripts, and mock HCM routes implemented
- auth dependencies implemented
- request and response schemas implemented
- API tests pass

### Gate 4: Release Candidate

Required:

- end-to-end tests pass
- coverage threshold passes
- docs are complete
- TRD exports to PDF successfully

## 9. Final Quality Checklist

- all required documents exist
- all required routes are implemented
- all protected routes enforce role constraints
- leave updates use explicit state transitions
- balances are scoped per employee and location
- HCM calls go through canonical adapter interface
- uncertain upstream outcomes lead to reconciliation flows
- script runs are persisted and queryable
- unit, integration, API, and end-to-end tests all pass
- coverage thresholds are enforced
- docs are exportable

## 10. Suggested Commands

```bash
make install
make run
make seed
make test
make test-unit
make test-integration
make test-api
make test-e2e
make export-docs
```