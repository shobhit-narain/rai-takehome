# Time-Off Microservice Technical Requirements Document

## 1. Document Information

- Project: Time-Off Microservice
- Primary stack: Python, FastAPI, SQLite
- Supporting libraries: SQLAlchemy, Pydantic, httpx, APScheduler, pytest
- Status: Draft
- Intended deliverable format: Markdown source, PDF export for submission

## 2. Overview

ReadyOn needs a backend service that allows employees to view leave balances and request time off while allowing managers to review and act on those requests. The external Human Capital Management system is the source of truth for employment data and leave balances, so the service must preserve local workflow usability without losing consistency with the HCM.

The core problem is balance integrity. An employee may request leave in ReadyOn while a separate system updates the HCM balance independently, for example due to work anniversary accruals or year-end refreshes. The service must support local request lifecycle management, real-time HCM interactions, batch balance synchronization, and defensive reconciliation when external validation is incomplete or delayed.

## 3. Product Context

ReadyOn is the primary employee-facing interface for time-off requests. The HCM remains authoritative for balance values and other employment data. The service must support:

- employee self-service leave workflows
- manager review and approval workflows
- real-time HCM validation and mutation calls
- batch HCM balance ingestion
- local defensive checks when HCM validation cannot be fully trusted
- mock HCM endpoints for testing and simulation

## 4. Goals

The service will:

- authenticate employee, manager, and admin users
- expose leave-related REST endpoints
- persist leave requests and local balance records in SQLite
- synchronize with HCM through a canonical adapter layer
- provide resilient HTTP communication for HCM calls
- provide caching and rate-limit coordination
- support scheduled reconciliation and backfill jobs
- include a strong automated test suite for regression protection

## 5. Non-Goals

The initial implementation will not include:

- production single sign-on integration
- distributed message queues
- multi-region deployment
- production Redis cluster deployment
- production Airflow deployment
- payroll or compensation logic
- a user interface

## 6. Users and Roles

### Employee

The employee wants to:

- view an accurate leave balance
- request leave with immediate feedback
- view current and recent leave requests
- cancel or modify eligible requests

### Manager

The manager wants to:

- review pending leave requests for managed employees
- approve or deny requests with confidence that data is valid
- view relevant balances and request status before making decisions

### Admin

The admin wants to:

- perform privileged review and correction actions
- run reconciliation and maintenance scripts
- inspect system state during failures or support workflows

## 7. Functional Requirements

### 7.1 Authentication and Authorization

The system must support authenticated users with personas:

- employee
- manager
- admin

All protected endpoints must resolve a `LoggedInUser` object with at least:

- `user_id`
- `role`
- `manager_id`
- `location_id`

The authenticated user object must expose helper methods:

- `is_employee()`
- `is_manager()`
- `is_admin()`

Authorization rules:

- employees may access only their own leave data
- managers may act only on employees in their reporting tree
- admins may access all records
- all privileged actions must be auditable

### 7.2 Leave Endpoints

#### Employee endpoints

- `GET /leaves/balance`
- `GET /leaves/current`
- `POST /leaves/request`
- `POST /leaves/{leave_id}/update`

#### Manager endpoints

- `GET /leaves/requests`
- `POST /leaves/{leave_id}/update`

### 7.3 Database

The system must use SQLite for local persistence.

Required logical tables:

- `users`
- `leave_requests`
- `leave_balances`
- `hcm_configs`
- `script_runs`
- `audit_events`

Balances must be maintained per employee per location.

### 7.4 HCM Adapter Layer

The system must provide canonical methods:

- `get_balances(user_id, location_id=None)`
- `batch_get_balances(request)`
- `create_leave(user_id, leave_request)`
- `update_leave(actor_user_id, update_request)`

HCM-specific adapters must convert canonical requests into provider-specific formats.

### 7.5 HTTP Wrapper

The system must provide an HTTP wrapper with methods:

- `get`
- `post`
- `put`
- `delete`

The wrapper must support:

- error normalization
- exponential backoff with jitter
- retry for transient failures
- rate-limit parsing from response headers
- typed upstream exceptions
- optional response caching for test or mock flows only

### 7.6 Cache Layer

The system must provide:

- `get_key(namespace, key)`
- `set_key(namespace, key, value, ttl=None)`
- `delete_key(namespace, key)`
- `get_ratelimit(provider)`
- `acquire_ratelimit(provider, tokens=1)`
- `update_ratelimit_from_headers(provider, headers)`

The initial backend may be in-memory. The interface must allow later Redis implementation.

### 7.7 Scheduling and Scripts

The system must provide a scheduling and scripts module with methods:

- `run_script(name, params)`
- `schedule_script(name, cron_expression, params)`
- `get_status(run_id)`
- `cancel_run(run_id)`

The initial scheduler implementation may use APScheduler. The scheduling API must be written so other runners can be added later.

### 7.8 Mock HCM

The service must include mock HCM endpoints with stateful logic to simulate:

- successful balance lookup
- successful leave creation
- insufficient balance
- invalid dimensions
- delayed consistency
- independent balance refresh events
- intermittent validation gaps

### 7.9 Testing

The service must include:

- unit tests
- integration tests
- API tests
- end-to-end tests

The test suite must validate behavior around synchronization, authorization, state transitions, retries, rate-limits, and reconciliation.

## 8. Non-Functional Requirements

### 8.1 Correctness

Correctness is the highest priority. The service must not silently accept inconsistent state between local data and HCM. If the final truth is uncertain, the system must mark the record for reconciliation.

### 8.2 Testability

All infrastructure dependencies must be injectable or replaceable in tests. Service boundaries must remain narrow and explicit.

### 8.3 Maintainability

The codebase must be structured into modules with one primary responsibility each. Domain logic must not be duplicated in routes or repositories.

### 8.4 Observability

The system must log:

- request identifiers
- user identifiers
- leave request identifiers
- HCM provider identifiers
- external request identifiers
- script run identifiers
- transition and error outcomes

Sensitive actions must produce audit events.

## 9. Recommended Architecture

The service will be implemented as a modular monolith.

Top-level architectural areas:

- API layer
- auth layer
- domain layer
- service layer
- repository layer
- adapter layer
- infrastructure layer
- jobs layer
- mock HCM layer
- tests

### 9.1 API Layer

Responsible for:

- HTTP routing
- request validation
- response serialization
- dependency wiring
- exception mapping

The API layer must remain thin and delegate business behavior to services.

### 9.2 Auth Layer

Responsible for:

- resolving authenticated users
- role-aware dependencies
- helper methods for current-user checks

The auth layer must not contain leave business rules.

### 9.3 Domain Layer

Responsible for:

- leave status definitions
- state transition rules
- business policy validation
- canonical domain models

The domain layer must be pure and testable without HTTP or database dependencies.

### 9.4 Service Layer

Responsible for orchestration:

- leave request creation
- leave updates
- balance reads and updates
- reconciliation
- audit emission
- script execution logic

### 9.5 Repository Layer

Responsible for persistence only:

- querying users
- querying and updating leave requests
- querying and upserting balances
- persisting script runs
- persisting audit events

### 9.6 Adapter Layer

Responsible for:

- canonical HCM interfaces
- provider-specific request mapping
- provider-specific response mapping

### 9.7 Infrastructure Layer

Responsible for:

- database session management
- HTTP client implementation
- retry policy
- cache backend
- rate-limit support

### 9.8 Jobs Layer

Responsible for:

- scheduled execution
- script registration
- run tracking
- reconciliation orchestration

### 9.9 Mock HCM Layer

Responsible for:

- upstream simulation for tests
- scenario switching
- stateful external truth models

## 10. Data Model

### 10.1 users

Fields:

- `id`
- `email`
- `name`
- `role`
- `manager_id`
- `location_id`
- `is_active`
- `created_ts`
- `updated_ts`

### 10.2 leave_requests

Fields:

- `id`
- `external_hcm_id`
- `requestor_id`
- `approver_id`
- `location_id`
- `leave_type`
- `leave_duration`
- `leave_start`
- `leave_end`
- `status`
- `failure_reason`
- `version`
- `created_ts`
- `updated_ts`
- `approved_ts`
- `complete_ts`
- `last_synced_ts`

### 10.3 leave_balances

Fields:

- `id`
- `user_id`
- `location_id`
- `leave_type`
- `num_available`
- `num_ytd_taken`
- `num_limit`
- `external_updated_ts`
- `updated_ts`

Uniqueness rule:

- unique on `user_id`, `location_id`, `leave_type`

### 10.4 hcm_configs

Fields:

- `id`
- `provider_name`
- `base_url`
- `auth_type`
- `token_ref`
- `rate_limit_default`
- `is_active`
- `created_ts`
- `updated_ts`

### 10.5 script_runs

Fields:

- `id`
- `script_name`
- `status`
- `schedule_expression`
- `params_json`
- `started_ts`
- `finished_ts`
- `cancel_requested`
- `error_message`

### 10.6 audit_events

Fields:

- `id`
- `entity_type`
- `entity_id`
- `action`
- `actor_user_id`
- `payload_json`
- `created_ts`

## 11. Leave Lifecycle and State Machine

Leave status values:

- `created`
- `requested`
- `approved`
- `denied`
- `complete`
- `canceled`
- `pending_reconciliation`

Allowed transitions:

- `created -> requested`
- `requested -> approved`
- `requested -> denied`
- `requested -> canceled`
- `approved -> canceled` when policy permits
- `approved -> complete`
- `any -> pending_reconciliation` when external confirmation is ambiguous
- `pending_reconciliation -> approved`
- `pending_reconciliation -> denied`
- `pending_reconciliation -> canceled`
- `pending_reconciliation -> complete`

The state machine must be implemented explicitly and tested directly.

## 12. API Behavior

### 12.1 GET /leaves/balance

Returns balances for the authenticated user. Results must be scoped by the user and location context.

### 12.2 GET /leaves/current

Returns current and recent leave requests for the authenticated user.

### 12.3 POST /leaves/request

Creates a leave request.

Expected behavior:

1. validate request shape
2. validate ownership and supported leave type
3. validate date range and duration
4. consult balance and HCM adapter
5. persist local record
6. emit audit event
7. return canonical result

### 12.4 POST /leaves/{leave_id}/update

Allows employee, manager, or admin action depending on role and target state.

Employee actions may include:

- cancel
- modify

Manager actions may include:

- approve
- deny
- request_change

Admin actions may include:

- override actions for support or repair

### 12.5 GET /leaves/requests

Returns a manager-scoped or admin-scoped list of leave requests.

## 13. Canonical HCM Interface

The canonical HCM interface will be defined as a Python protocol.

Required methods:

- `get_balances`
- `batch_get_balances`
- `create_leave`
- `update_leave`

This interface isolates the domain and service layers from provider-specific details.

## 14. Error Handling

The API must return a stable JSON error envelope:

```json
{
  "code": "STRING_CODE",
  "message": "Human readable message",
  "details": {},
  "request_id": "uuid-or-similar"
}
```

Representative error codes:

- `AUTH_REQUIRED`
- `ACCESS_DENIED`
- `VALIDATION_ERROR`
- `INVALID_STATE_TRANSITION`
- `INSUFFICIENT_BALANCE`
- `UPSTREAM_TIMEOUT`
- `UPSTREAM_RATE_LIMITED`
- `UPSTREAM_VALIDATION_ERROR`
- `RECONCILIATION_REQUIRED`

## 15. Logging and Audit

Each request should carry a request identifier.

Structured logs should include, where applicable:

- `request_id`
- `user_id`
- `role`
- `leave_request_id`
- `provider`
- `external_request_id`
- `script_run_id`
- `action`
- `result`
- `latency_ms`

Audit events must be written for:

- leave creation
- approval
- denial
- cancellation
- admin overrides
- reconciliation outcomes

## 16. Seeded Data

The initial dataset must include:

- about 5000 employees
- one or two leave types
- manager relationships for all employees except one top-level exception
- multiple locations
- seeded balances per user and location
- seeded leave requests across several statuses
- seeded HCM config records

The mock HCM data must be maintained separately so local and external states can diverge during tests.

## 17. Scheduling and Scripts

Built-in scripts:

- `sync_all_balances`
- `reconcile_recent_leaves`
- `backfill_balances`
- `repair_pending_reconciliation`

Every script run must persist a `script_runs` record and expose current status.

## 18. Acceptance Criteria

### 18.1 Authentication and Authorization

- unauthenticated requests to protected routes return 401
- employee users can act only on their own leave records
- manager users can act only on managed employees
- admin users can access all leave and script routes

### 18.2 Leave Lifecycle

- valid leave request persists and calls the HCM adapter
- invalid leave type or date range fails validation
- invalid state transitions are rejected
- uncertain HCM outcomes move the leave request to `pending_reconciliation`

### 18.3 Balances and Sync

- balances are unique per employee, location, and leave type
- real-time balance lookup is supported
- batch balance synchronization is supported
- reconciliation can repair local state after external balance changes

### 18.4 Adapter and HTTP Wrapper

- canonical adapter hides provider-specific payloads
- retry and backoff behavior is covered by tests
- rate-limit headers are parsed and persisted through cache
- response caching is disabled by default and only used for tests or mock flows

### 18.5 Scheduling

- scripts can run ad hoc
- scripts can be scheduled
- script status can be queried
- cancellation requests are persisted
- reconciliation jobs can run end-to-end in tests

### 18.6 Testing

- unit, integration, API, and end-to-end tests are present
- mock HCM endpoints support scenario simulation
- coverage thresholds are enforced in CI

## 19. Alternatives Considered

### Flask

Flask aligns well with decorator-based auth patterns, but FastAPI provides stronger request validation, dependency injection, and test override support.

### Django

Django provides a powerful framework, but it is heavier than necessary for this service and adds surface area unrelated to the sync and reconciliation problem.

### Event-Driven Queue-First Architecture

A queue-first design may improve scalability but adds complexity and weakens immediate request feedback for employees. For this scope, synchronous orchestration plus reconciliation jobs is the preferred tradeoff.

## 20. Risks and Mitigations

### Local and HCM state drift

Mitigation:

- reconciliation status
- scheduled sync jobs
- audit events
- explicit sync timestamps

### Race conditions between approval and cancellation

Mitigation:

- optimistic concurrency with version fields
- deterministic update rules
- conflict-aware tests

### Manager hierarchy bugs

Mitigation:

- isolated hierarchy repository methods
- direct unit and integration tests

### Retry or rate-limit logic misbehavior

Mitigation:

- dedicated HTTP wrapper tests
- deterministic fake headers and clocks

### Over-mocking

Mitigation:

- real SQLite integration tests
- end-to-end flows using mock HCM routes
