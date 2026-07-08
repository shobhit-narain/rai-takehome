# Test Plan

## 1. Purpose

This document defines the testing strategy for the Python Time-Off Microservice. The goal is to detect regressions in authorization, leave lifecycle behavior, HCM synchronization, retry logic, rate-limit handling, and reconciliation flows.

## 2. Objectives

The test suite must prove that the service:

- enforces authentication and authorization correctly
- preserves valid leave state transitions
- prevents invalid transitions
- stores balances per employee and location
- integrates correctly with the canonical HCM adapter
- handles rate-limits and transient upstream failures correctly
- reconciles local state when HCM truth changes independently
- records script execution and supports scheduled jobs
- remains stable under concurrent or conflicting update scenarios

## 3. Test Stack

- `pytest`
- `pytest-cov`
- FastAPI `TestClient`
- SQLite test databases
- dependency overrides for test injection
- HTTP mocks or local mock HCM routes for upstream simulation

## 4. Layers

### Unit Tests

Unit tests validate isolated modules without real database or HTTP dependencies unless the module is itself infrastructure.

### Integration Tests

Integration tests validate repository and service behavior against real SQLite and real object wiring, while external HCM dependencies are simulated.

### API Tests

API tests validate route contracts, auth enforcement, request validation, response shapes, and dependency wiring using the web application interface.

### End-to-End Tests

End-to-end tests validate complete business workflows, including mock HCM scenarios, scheduled scripts, and reconciliation behavior.

## 5. Directory Layout

```text
tests/
  conftest.py
  helpers/
    app_factory.py
    auth.py
    db.py
    fixtures.py
    mock_hcm.py
    overrides.py

  unit/
    test_auth_dependencies.py
    test_logged_in_user.py
    test_leave_state_machine.py
    test_leave_policy_service.py
    test_balances_service.py
    test_http_client.py
    test_retry_policy.py
    test_rate_limit_service.py
    test_cache_service.py
    test_mock_hcm_adapter.py
    test_scripts_service.py
    test_reconciliation_service.py

  integration/
    test_users_repository.py
    test_leave_requests_repository.py
    test_leave_balances_repository.py
    test_hcm_configs_repository.py
    test_script_runs_repository.py
    test_audit_events_repository.py
    test_leaves_service_integration.py
    test_balances_service_integration.py
    test_reconciliation_integration.py
    test_mock_hcm_adapter_integration.py

  api/
    test_health_routes.py
    test_leaves_employee_routes.py
    test_leaves_manager_routes.py
    test_leaves_admin_routes.py
    test_scripts_routes.py
    test_mock_hcm_routes.py

  e2e/
    test_employee_request_happy_path.py
    test_employee_request_insufficient_balance.py
    test_external_balance_refresh.py
    test_manager_approval_flow.py
    test_manager_denial_flow.py
    test_employee_cancel_flow.py
    test_cancel_vs_approve_race.py
    test_ambiguous_hcm_response.py
    test_rate_limit_retry_flow.py
    test_scheduled_sync_all_balances.py
    test_repair_pending_reconciliation.py
```

## 6. Fixtures

### Global Fixtures

Global fixtures provide:

- a clean test database
- seeded users
- seeded balances
- seeded manager hierarchy
- seeded HCM config
- reusable authenticated users
- app factory instances
- dependency override helpers

### App Fixtures

App fixtures support:

- real services with test database
- overridden auth dependencies
- overridden HCM adapter dependencies
- scenario-specific mock HCM behavior
- cleanup of FastAPI dependency overrides after each test

### Data Fixtures

Data fixtures include:

- employee user
- manager user
- admin user
- employee with low balance
- employee with pending request
- employee with approved request
- employee in another manager tree
- location-specific balance data

## 7. Unit Test Coverage

### Auth Dependencies

`tests/unit/test_auth_dependencies.py`

Cases:

- missing bearer token returns auth error
- invalid bearer token returns auth error
- valid token resolves authenticated user
- employee dependency accepts employee role
- manager dependency rejects employee role
- manager dependency accepts manager role
- admin dependency rejects non-admin role

### LoggedInUser

`tests/unit/test_logged_in_user.py`

Cases:

- `is_employee()` returns true only for employee
- `is_manager()` returns true only for manager
- `is_admin()` returns true only for admin

### Leave State Machine

`tests/unit/test_leave_state_machine.py`

Cases:

- `created -> requested` is valid
- `requested -> approved` is valid
- `requested -> denied` is valid
- `requested -> canceled` is valid
- `approved -> complete` is valid
- `approved -> denied` is valid (with mitigating circumstances)
- invalid transitions raise domain error
- uncertain result can move to `pending_reconciliation`
- reconciliation completion transitions are valid

### Leave Policy Service

`tests/unit/test_leave_policy_service.py`

Cases:

- employee can request leave for self
- employee cannot request leave for another user
- manager can approve direct report
- manager can approve indirect report if policy allows reporting tree traversal
- manager cannot approve unrelated employee
- admin override is permitted
- unsupported leave type is rejected
- invalid date range is rejected

### Balances Service

`tests/unit/test_balances_service.py`

Cases:

- balance read is scoped by user and location
- balance upsert preserves uniqueness semantics
- reconciliation update applies external values correctly
- batch upsert handles mixed insert and update rows

### HTTP Client

`tests/unit/test_http_client.py`

Cases:

- successful GET returns parsed response
- transient error retries according to policy
- non-retriable error does not retry
- timeout raises typed upstream timeout error
- authentication failure raises typed upstream auth error
- rate-limit response updates rate-limit state

### Retry Policy

`tests/unit/test_retry_policy.py`

Cases:

- retry count obeys configured max attempts
- backoff duration grows exponentially
- jitter value is applied within expected range
- non-retriable exception returns false from retry predicate

### Rate Limit Service

`tests/unit/test_rate_limit_service.py`

Cases:

- empty state returns no quota
- header parser extracts reset and remaining values
- acquire succeeds when tokens available
- acquire fails when tokens unavailable
- update persists new state through cache

### Cache Service

`tests/unit/test_cache_service.py`

Cases:

- get on missing key returns null-like value
- set then get returns stored value
- namespace isolation works
- TTL expiration removes key
- delete removes key

### Mock HCM Adapter

`tests/unit/test_mock_hcm_adapter.py`

Cases:

- create leave maps canonical request correctly
- update leave maps canonical action correctly
- get balances returns canonical balance list
- insufficient balance response maps to business result
- ambiguous response maps to reconciliation-needed result

### Scripts Service

`tests/unit/test_scripts_service.py`

Cases:

- known script starts successfully
- unknown script fails with stable error
- status lookup returns current state
- cancel request marks run for cancellation

### Reconciliation Service

`tests/unit/test_reconciliation_service.py`

Cases:

- pending reconciliation request can be rechecked
- external approved state repairs local pending record
- external denied state repairs local pending record
- missing external record creates predictable failure path

## 8. Integration Test Coverage

### Users Repository

`tests/integration/test_users_repository.py`

Cases:

- find user by id
- find manager for employee
- retrieve reporting tree
- unrelated manager tree exclusion works

### Leave Requests Repository

`tests/integration/test_leave_requests_repository.py`

Cases:

- create leave request
- update leave request version
- filter by requestor
- filter by manager scope
- pagination works
- status filtering works

### Leave Balances Repository

`tests/integration/test_leave_balances_repository.py`

Cases:

- insert balance row
- enforce unique user-location-leave-type constraint
- upsert existing balance
- query by user and location
- bulk upsert works

### HCM Configs Repository

`tests/integration/test_hcm_configs_repository.py`

Cases:

- active config lookup works
- provider-specific config retrieval works

### Script Runs Repository

`tests/integration/test_script_runs_repository.py`

Cases:

- create script run
- update status
- set cancel request
- retrieve run status

### Audit Events Repository

`tests/integration/test_audit_events_repository.py`

Cases:

- create audit event
- query audit events by entity
- query audit events by actor

### Leaves Service Integration

`tests/integration/test_leaves_service_integration.py`

Cases:

- employee request persists local record and audit event
- manager approval updates approver and status
- employee cancel updates eligible request
- invalid state transition fails without corrupting row
- conflicting update detects version mismatch

### Balances Service Integration

`tests/integration/test_balances_service_integration.py`

Cases:

- read local balances
- batch update balances from canonical external data
- preserve location scoping

### Reconciliation Integration

`tests/integration/test_reconciliation_integration.py`

Cases:

- local pending request repaired from external approved state
- local pending request repaired from external denied state
- local balance drift corrected after external refresh

### Mock HCM Adapter Integration

`tests/integration/test_mock_hcm_adapter_integration.py`

Cases:

- create leave against mock HCM store
- update leave against mock HCM store
- batch balance read from mock HCM store
- scenario toggles alter behavior as expected

## 9. API Test Coverage

### Employee Leave Routes

`tests/api/test_leaves_employee_routes.py`

Cases:

- employee can fetch own balances
- employee can fetch own current requests
- employee can submit valid leave request
- employee cannot submit leave for another user
- invalid payload returns validation error
- unauthenticated request returns 401
- employee cannot list manager queue

### Manager Leave Routes

`tests/api/test_leaves_manager_routes.py`

Cases:

- manager can list requests for own reporting tree
- manager can approve pending request
- manager can deny pending request
- manager cannot update unrelated employee request
- non-manager cannot access manager queue

### Admin Leave Routes

`tests/api/test_leaves_admin_routes.py`

Cases:

- admin can inspect any request if route is exposed
- admin can perform permitted override action
- admin action produces audit event

### Scripts Routes

`tests/api/test_scripts_routes.py`

Cases:

- admin can run script
- non-admin cannot run script
- admin can query script status
- admin can request cancellation
- invalid script name returns stable error

### Mock HCM Routes

`tests/api/test_mock_hcm_routes.py`

Cases:

- balance lookup returns seeded data
- create leave route mutates mock HCM state
- update leave route mutates mock HCM state
- scenario activation changes route behavior

## 10. End-to-End Test Coverage

### Employee Request Happy Path

`tests/e2e/test_employee_request_happy_path.py`

Scenario:

1. authenticate employee
2. fetch balance
3. submit valid leave request
4. verify local leave row
5. verify audit event
6. verify external mock HCM record

### Employee Request With Insufficient Balance

`tests/e2e/test_employee_request_insufficient_balance.py`

Scenario:

1. authenticate low-balance employee
2. submit leave request exceeding balance
3. verify stable error response
4. verify local state remains consistent

### External Balance Refresh

`tests/e2e/test_external_balance_refresh.py`

Scenario:

1. seed local and external balances
2. apply anniversary refresh in mock HCM
3. run reconciliation or sync script
4. verify local balance matches external truth

### Manager Approval Flow

`tests/e2e/test_manager_approval_flow.py`

Scenario:

1. employee submits leave request
2. manager lists queue
3. manager approves request
4. verify local status
5. verify approver assignment
6. verify external update succeeded

### Manager Denial Flow

`tests/e2e/test_manager_denial_flow.py`

Scenario:

1. employee submits leave request
2. manager denies request
3. verify denial state and audit event

### Employee Cancel Flow

`tests/e2e/test_employee_cancel_flow.py`

Scenario:

1. employee creates cancelable request
2. employee cancels request
3. verify local and external state

### Cancel vs Approve Race

`tests/e2e/test_cancel_vs_approve_race.py`

Scenario:

1. create request
2. issue employee cancel and manager approve near-simultaneously
3. verify one deterministic winning path
4. verify no silent overwrite
5. verify final state is valid

### Ambiguous HCM Response

`tests/e2e/test_ambiguous_hcm_response.py`

Scenario:

1. configure mock HCM to return ambiguous success
2. create or update leave
3. verify local status becomes `pending_reconciliation`
4. run repair script
5. verify final resolved state

### Rate-Limit Retry Flow

`tests/e2e/test_rate_limit_retry_flow.py`

Scenario:

1. configure mock HCM to emit retryable failures and rate-limit headers
2. execute request through service
3. verify retries occurred
4. verify rate-limit state updated
5. verify final outcome

### Scheduled Sync All Balances

`tests/e2e/test_scheduled_sync_all_balances.py`

Scenario:

1. schedule balance sync script
2. trigger scheduler execution
3. verify run record
4. verify balances updated

### Repair Pending Reconciliation

`tests/e2e/test_repair_pending_reconciliation.py`

Scenario:

1. seed pending reconciliation records
2. configure external truth
3. run repair script
4. verify final states and audit events

## 11. Test Data Rules

- used deterministic seeds where possible
- isolated tests by database or transaction strategy
- reset dependency overrides after each test
- avoided hidden global state
- separated local seeded state from mock external HCM state
- used stable time helpers for timestamp-sensitive tests

## 12. CI Requirements

The CI pipeline runs:

- unit tests
- integration tests
- API tests
- end-to-end tests
- coverage threshold enforcement

The pipeline should fail if:

- any test fails
- coverage threshold is missed
- schema or seed flow breaks from a clean environment

## Exit Criteria

The test plan is complete:

- ✅ all planned test files exist
- ✅ critical workflows are covered at more than one layer
- ✅ mock HCM scenarios are usable in automated tests
- ✅ race and reconciliation behaviors are explicitly verified
- ✅ CI enforces quality gates