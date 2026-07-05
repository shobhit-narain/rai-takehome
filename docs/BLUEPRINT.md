# Time-Off Microservice Repository Blueprint

## 1. Purpose

This document defines the repository structure, file ownership, class and interface inventory, and test file plan for the Python Time-Off Microservice.

The blueprint is optimized for:

- a small number of implementation agents
- low coordination overhead
- explicit module boundaries
- strong testability
- predictable code generation

The implementation plan assumes three agents:

- Agent 1: foundation and infrastructure
- Agent 2: domain and application logic
- Agent 3: API and test harness

## 2. Repository Layout

```text
repo/
  docs/
    TRD.md
    IMPLEMENTATION_PLAN.md
    TEST_PLAN.md
    API_SPEC.md
    REPO_BLUEPRINT.md
    EXPORT.md

  src/
    app/
      __init__.py
      main.py
      config.py
      dependencies.py
      exceptions.py
      logging.py
      middleware.py

    api/
      __init__.py
      routers/
        __init__.py
        health.py
        leaves.py
        scripts.py
        mock_hcm.py
      schemas/
        __init__.py
        common.py
        auth.py
        leaves.py
        scripts.py
        hcm.py

    auth/
      __init__.py
      current_user.py
      dependencies.py
      tokens.py
      exceptions.py

    domain/
      __init__.py
      enums.py
      errors.py
      leave_state_machine.py
      leave_policy.py
      models.py

    services/
      __init__.py
      users_service.py
      balances_service.py
      leaves_service.py
      reconciliation_service.py
      scripts_service.py
      audit_service.py

    repositories/
      __init__.py
      users_repository.py
      leave_requests_repository.py
      leave_balances_repository.py
      hcm_configs_repository.py
      script_runs_repository.py
      audit_events_repository.py

    adapters/
      __init__.py
      hcm/
        __init__.py
        port.py
        canonical_models.py
        mapper.py
        mock_hcm_adapter.py
        workday_adapter.py
        sap_adapter.py

    infra/
      __init__.py
      db/
        __init__.py
        base.py
        session.py
        models.py
        seed.py
        factories.py
      http/
        __init__.py
        client.py
        retry.py
        errors.py
      cache/
        __init__.py
        interfaces.py
        inmemory_cache.py
        redis_stub.py
        ratelimit.py
      jobs/
        __init__.py
        scheduler.py
        registry.py
        runners.py
        scripts.py

  tests/
    conftest.py
    helpers/
      app_factory.py
      auth.py
      db.py
      fixtures.py
      mock_hcm.py
      overrides.py
      clocks.py

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

  scripts/
    seed_local_db.py
    reset_local_db.py
    export_docs.sh

  pyproject.toml
  README.md
  Makefile
```

## 3. Agent Ownership Summary

### Agent 1: Foundation and Infrastructure

Owns:

- `src/app` bootstrap and shared plumbing
- `src/infra` packages
- `src/repositories`
- database models and session management
- seed and factory tooling
- cache, HTTP client, retry, and scheduler base
- repository and infrastructure tests

Must not own:

- leave policy logic
- service orchestration logic
- route handlers

### Agent 2: Domain and Application Logic

Owns:

- `src/auth/current_user.py`
- `src/domain`
- `src/services`
- `src/adapters/hcm`
- built-in script logic in `src/infra/jobs/scripts.py`
- domain, service, adapter, and reconciliation tests

Must not own:

- ORM definitions
- app bootstrap
- FastAPI route declarations

### Agent 3: API and Test Harness

Owns:

- `src/api`
- `src/auth/dependencies.py`
- `src/auth/tokens.py`
- `src/auth/exceptions.py`
- `src/app/dependencies.py`
- API exception mapping
- test app factory and dependency overrides
- API and end-to-end tests
- CI-facing test and docs export glue

Must not own:

- domain rule duplication
- direct persistence logic outside supported repositories and test setup

## 4. File-by-File Blueprint

### 4.1 Application Bootstrap

#### `src/app/main.py`

Purpose:

- create and configure the FastAPI application
- register routers
- register middleware
- register exception handlers

Primary symbols:

- `create_app() -> FastAPI`
- `app`

Dependencies:

- settings
- middleware
- routers
- exception handlers

Owner:

- Agent 1

#### `src/app/config.py`

Purpose:

- define runtime configuration

Primary classes:

- `AppSettings`

Suggested fields:

- `app_name`
- `environment`
- `sqlite_url`
- `default_hcm_provider`
- `enable_response_cache`
- `log_level`

Owner:

- Agent 1

#### `src/app/dependencies.py`

Purpose:

- centralize shared dependency providers for services and infrastructure

Primary functions:

- `get_settings()`
- `get_db_session()`
- `get_cache_backend()`
- `get_rate_limit_service()`
- `get_http_client()`
- `get_users_service()`
- `get_balances_service()`
- `get_leaves_service()`
- `get_reconciliation_service()`
- `get_scripts_service()`
- `get_hcm_service()`

Owner:

- Agent 3

#### `src/app/exceptions.py`

Purpose:

- shared application-level exception types
- common exception payload helpers

Primary classes:

- `AppError`
- `AuthRequiredError`
- `AccessDeniedError`
- `ValidationFailedError`
- `ConflictError`
- `ResourceNotFoundError`
- `UpstreamDependencyError`

Owner:

- Agent 1

#### `src/app/logging.py`

Purpose:

- configure structured logging

Primary functions:

- `configure_logging()`
- `get_logger(name: str)`

Owner:

- Agent 1

#### `src/app/middleware.py`

Purpose:

- request ID middleware
- request context helpers

Primary classes:

- `RequestIdMiddleware`

Owner:

- Agent 1

### 4.2 API Routers

#### `src/api/routers/health.py`

Purpose:

- health and readiness endpoints

Primary functions:

- `get_health()`
- `get_readiness()`

Owner:

- Agent 3

#### `src/api/routers/leaves.py`

Purpose:

- employee, manager, and admin leave routes

Primary functions:

- `get_balance()`
- `get_current_leaves()`
- `request_leave()`
- `update_leave_request()`
- `get_leave_requests()`

Expected dependencies:

- `require_authenticated_user`
- `require_manager_or_admin`
- `LeavesService`
- `BalancesService`

Owner:

- Agent 3

#### `src/api/routers/scripts.py`

Purpose:

- ad hoc and scheduled script routes

Primary functions:

- `run_script()`
- `schedule_script()`
- `get_script_status()`
- `cancel_script_run()`

Expected dependencies:

- `require_admin`
- `ScriptsService`

Owner:

- Agent 3

#### `src/api/routers/mock_hcm.py`

Purpose:

- mock external HCM endpoints for testing and simulation

Primary functions:

- `get_mock_balances()`
- `create_mock_leave()`
- `update_mock_leave()`
- `activate_mock_scenario()`

Expected dependencies:

- `require_admin`
- `HcmServicePort` or mock HCM service

Owner:

- Agent 3

### 4.3 API Schemas

#### `src/api/schemas/common.py`

Purpose:

- shared response and error models

Primary classes:

- `ErrorResponse`
- `PaginationMeta`
- `PagedResponse`

Owner:

- Agent 3

#### `src/api/schemas/auth.py`

Purpose:

- auth-facing response models

Primary classes:

- `AuthenticatedUserResponse`

Owner:

- Agent 3

#### `src/api/schemas/leaves.py`

Purpose:

- leave endpoint request and response models

Primary classes:

- `LeaveBalanceResponse`
- `LeaveRequestResponse`
- `LeaveCreateRequest`
- `LeaveUpdateRequest`
- `LeaveListResponse`
- `ManagerLeaveQueryParams`

Owner:

- Agent 3

#### `src/api/schemas/scripts.py`

Purpose:

- script endpoint request and response models

Primary classes:

- `RunScriptRequest`
- `ScheduleScriptRequest`
- `ScriptRunResponse`
- `CancelScriptResponse`

Owner:

- Agent 3

#### `src/api/schemas/hcm.py`

Purpose:

- mock HCM request and response models

Primary classes:

- `MockHcmBalanceResponse`
- `MockHcmLeaveCreateRequest`
- `MockHcmLeaveUpdateRequest`
- `MockScenarioActivationRequest`
- `MockScenarioActivationResponse`

Owner:

- Agent 3

### 4.4 Auth Package

#### `src/auth/current_user.py`

Purpose:

- define authenticated user model used across services and dependencies

Primary classes:

- `LoggedInUser`

Suggested fields:

- `user_id`
- `role`
- `manager_id`
- `location_id`

Suggested methods:

- `is_employee()`
- `is_manager()`
- `is_admin()`

Owner:

- Agent 2

#### `src/auth/dependencies.py`

Purpose:

- FastAPI dependencies for authentication and authorization

Primary functions:

- `get_logged_in_user()`
- `require_authenticated_user()`
- `require_employee()`
- `require_manager_or_admin()`
- `require_admin()`

Owner:

- Agent 3

#### `src/auth/tokens.py`

Purpose:

- resolve bearer tokens into local user context

Primary classes:

- `TokenResolver`

Primary methods:

- `resolve_bearer_token(token: str) -> LoggedInUser | None`

Owner:

- Agent 3

#### `src/auth/exceptions.py`

Purpose:

- auth-specific errors

Primary classes:

- `InvalidTokenError`
- `MissingTokenError`
- `ForbiddenRoleError`

Owner:

- Agent 3

### 4.5 Domain Package

#### `src/domain/enums.py`

Purpose:

- enums for roles, leave types, statuses, actions, and script states

Primary classes:

- `UserRole`
- `LeaveType`
- `LeaveStatus`
- `LeaveAction`
- `ScriptRunStatus`

Owner:

- Agent 2

#### `src/domain/errors.py`

Purpose:

- domain-specific exceptions

Primary classes:

- `DomainError`
- `InvalidStateTransitionError`
- `PolicyViolationError`
- `InsufficientBalanceError`
- `ReconciliationRequiredError`

Owner:

- Agent 2

#### `src/domain/leave_state_machine.py`

Purpose:

- explicit leave transition rules

Primary classes:

- `LeaveStateMachine`

Primary methods:

- `can_transition(current_status, action) -> bool`
- `next_status(current_status, action) -> LeaveStatus`

Owner:

- Agent 2

#### `src/domain/leave_policy.py`

Purpose:

- ownership, role, and manager-tree policy checks

Primary classes:

- `LeavePolicyService`

Primary methods:

- `validate_leave_request(actor, target_user_id, request)`
- `validate_leave_update(actor, leave_request, action, reporting_tree_user_ids)`

Owner:

- Agent 2

#### `src/domain/models.py`

Purpose:

- canonical domain models and commands

Primary classes:

- `LeaveRequestDomainModel`
- `LeaveBalanceDomainModel`
- `LeaveCreateCommand`
- `LeaveUpdateCommand`
- `ScriptRunDomainModel`

Owner:

- Agent 2

### 4.6 Services Package

#### `src/services/users_service.py`

Purpose:

- user lookup and reporting-tree orchestration

Primary classes:

- `UsersService`

Primary methods:

- `get_user(user_id)`
- `get_reporting_tree(manager_user_id)`
- `is_manager_of(manager_user_id, employee_user_id)`

Owner:

- Agent 2

#### `src/services/balances_service.py`

Purpose:

- local balance reads and updates
- batch balance reconciliation support

Primary classes:

- `BalancesService`

Primary methods:

- `get_user_balances(user_id, location_id=None)`
- `upsert_balance(balance_model)`
- `bulk_upsert_balances(balance_models)`
- `reconcile_balances(external_balances)`

Owner:

- Agent 2

#### `src/services/leaves_service.py`

Purpose:

- main leave workflow orchestration

Primary classes:

- `LeavesService`

Primary methods:

- `get_current_leaves(actor, filters=None)`
- `get_manager_leave_requests(actor, filters)`
- `request_leave(actor, command)`
- `update_leave_request(actor, leave_id, command)`

Owner:

- Agent 2

#### `src/services/reconciliation_service.py`

Purpose:

- repair local state from external truth

Primary classes:

- `ReconciliationService`

Primary methods:

- `reconcile_leave_request(leave_id)`
- `reconcile_recent_leaves()`
- `sync_all_balances()`
- `repair_pending_reconciliation()`

Owner:

- Agent 2

#### `src/services/scripts_service.py`

Purpose:

- orchestrate ad hoc and scheduled script execution

Primary classes:

- `ScriptsService`

Primary methods:

- `run_script(name, params)`
- `schedule_script(name, cron_expression, params)`
- `get_status(run_id)`
- `cancel_run(run_id)`

Owner:

- Agent 2

#### `src/services/audit_service.py`

Purpose:

- record audit events for sensitive actions

Primary classes:

- `AuditService`

Primary methods:

- `record_leave_created(actor, leave_request)`
- `record_leave_updated(actor, leave_request, action)`
- `record_reconciliation(actor_label, entity_id, result)`

Owner:

- Agent 2

### 4.7 Repositories Package

#### `src/repositories/users_repository.py`

Purpose:

- persistence methods for users and manager hierarchy

Primary classes:

- `UsersRepository`

Primary methods:

- `get_by_id(user_id)`
- `list_reports(manager_user_id)`
- `list_reporting_tree(manager_user_id)`

Owner:

- Agent 1

#### `src/repositories/leave_requests_repository.py`

Purpose:

- persistence methods for leave requests

Primary classes:

- `LeaveRequestsRepository`

Primary methods:

- `get_by_id(leave_id)`
- `list_by_requestor(user_id, filters=None)`
- `list_for_manager_scope(user_ids, filters=None)`
- `create(model)`
- `update(model)`
- `update_with_version_check(model, expected_version)`

Owner:

- Agent 1

#### `src/repositories/leave_balances_repository.py`

Purpose:

- persistence methods for balances

Primary classes:

- `LeaveBalancesRepository`

Primary methods:

- `list_for_user(user_id, location_id=None)`
- `upsert(balance_model)`
- `bulk_upsert(balance_models)`

Owner:

- Agent 1

#### `src/repositories/hcm_configs_repository.py`

Purpose:

- persistence methods for HCM config records

Primary classes:

- `HcmConfigsRepository`

Primary methods:

- `get_active_config(provider_name)`
- `list_active_configs()`

Owner:

- Agent 1

#### `src/repositories/script_runs_repository.py`

Purpose:

- persistence methods for script run records

Primary classes:

- `ScriptRunsRepository`

Primary methods:

- `create_run(script_name, params, schedule_expression=None)`
- `get_by_id(run_id)`
- `mark_started(run_id)`
- `mark_completed(run_id)`
- `mark_failed(run_id, error_message)`
- `request_cancel(run_id)`

Owner:

- Agent 1

#### `src/repositories/audit_events_repository.py`

Purpose:

- persistence methods for audit events

Primary classes:

- `AuditEventsRepository`

Primary methods:

- `create_event(event_model)`
- `list_by_entity(entity_type, entity_id)`
- `list_by_actor(actor_user_id)`

Owner:

- Agent 1

### 4.8 HCM Adapter Package

#### `src/adapters/hcm/port.py`

Purpose:

- canonical HCM interface

Primary symbols:

- `HcmServicePort`

Methods:

- `get_balances`
- `batch_get_balances`
- `create_leave`
- `update_leave`

Owner:

- Agent 2

#### `src/adapters/hcm/canonical_models.py`

Purpose:

- canonical HCM request and response models

Primary classes:

- `CanonicalBalance`
- `BatchBalanceRequest`
- `CanonicalLeaveCreateRequest`
- `CanonicalLeaveUpdateRequest`
- `CanonicalLeaveResult`

Owner:

- Agent 2

#### `src/adapters/hcm/mapper.py`

Purpose:

- map between internal models and provider payloads

Primary classes:

- `HcmMapper`

Primary methods:

- `to_create_payload()`
- `to_update_payload()`
- `to_canonical_balance()`
- `to_canonical_leave_result()`

Owner:

- Agent 2

#### `src/adapters/hcm/mock_hcm_adapter.py`

Purpose:

- mock HCM implementation for tests and local simulation

Primary classes:

- `MockHcmAdapter`

Primary methods:

- `get_balances()`
- `batch_get_balances()`
- `create_leave()`
- `update_leave()`

Owner:

- Agent 2

#### `src/adapters/hcm/workday_adapter.py`

Purpose:

- future provider adapter stub

Primary classes:

- `WorkdayAdapter`

Owner:

- Agent 2

#### `src/adapters/hcm/sap_adapter.py`

Purpose:

- future provider adapter stub

Primary classes:

- `SapAdapter`

Owner:

- Agent 2

### 4.9 Database Infrastructure

#### `src/infra/db/base.py`

Purpose:

- SQLAlchemy declarative base

Primary symbols:

- `Base`

Owner:

- Agent 1

#### `src/infra/db/session.py`

Purpose:

- database engine and session factory management

Primary functions:

- `build_engine()`
- `get_session_factory()`
- `get_db_session()`

Owner:

- Agent 1

#### `src/infra/db/models.py`

Purpose:

- SQLAlchemy ORM record definitions

Primary classes:

- `UserRecord`
- `LeaveRequestRecord`
- `LeaveBalanceRecord`
- `HcmConfigRecord`
- `ScriptRunRecord`
- `AuditEventRecord`

Owner:

- Agent 1

#### `src/infra/db/seed.py`

Purpose:

- deterministic seed orchestration

Primary classes:

- `SeedService`

Primary methods:

- `seed_users()`
- `seed_balances()`
- `seed_leave_requests()`
- `seed_hcm_configs()`
- `seed_all()`

Owner:

- Agent 1

#### `src/infra/db/factories.py`

Purpose:

- reusable DB record factories for tests and seed generation

Primary functions:

- `build_user_record()`
- `build_leave_request_record()`
- `build_leave_balance_record()`

Owner:

- Agent 1

### 4.10 HTTP Infrastructure

#### `src/infra/http/client.py`

Purpose:

- resilient HTTP wrapper

Primary classes:

- `HttpClient`

Primary methods:

- `get()`
- `post()`
- `put()`
- `delete()`

Owner:

- Agent 1

#### `src/infra/http/retry.py`

Purpose:

- retry decisions and delay calculation

Primary classes:

- `RetryPolicy`

Primary methods:

- `should_retry(exception_or_response)`
- `compute_delay(attempt_number)`

Owner:

- Agent 1

#### `src/infra/http/errors.py`

Purpose:

- typed upstream exceptions

Primary classes:

- `UpstreamTimeoutError`
- `UpstreamAuthError`
- `UpstreamRateLimitError`
- `UpstreamValidationError`
- `RetriableUpstreamError`

Owner:

- Agent 1

### 4.11 Cache Infrastructure

#### `src/infra/cache/interfaces.py`

Purpose:

- cache interface and rate-limit state models

Primary classes:

- `CacheBackend`
- `RateLimitState`

Owner:

- Agent 1

#### `src/infra/cache/inmemory_cache.py`

Purpose:

- in-memory cache implementation

Primary classes:

- `InMemoryCacheBackend`

Primary methods:

- `get_key()`
- `set_key()`
- `delete_key()`

Owner:

- Agent 1

#### `src/infra/cache/redis_stub.py`

Purpose:

- Redis-compatible stub backend

Primary classes:

- `RedisCacheBackendStub`

Owner:

- Agent 1

#### `src/infra/cache/ratelimit.py`

Purpose:

- rate-limit state coordination

Primary classes:

- `RateLimitService`

Primary methods:

- `get_ratelimit(provider)`
- `acquire_ratelimit(provider, tokens=1)`
- `update_ratelimit_from_headers(provider, headers)`

Owner:

- Agent 1

### 4.12 Jobs Infrastructure

#### `src/infra/jobs/scheduler.py`

Purpose:

- scheduler wrapper around APScheduler

Primary classes:

- `SchedulerService`

Primary methods:

- `start()`
- `shutdown()`
- `schedule_job()`
- `cancel_job()`

Owner:

- Agent 1

#### `src/infra/jobs/registry.py`

Purpose:

- named script registration

Primary classes:

- `ScriptRegistry`

Primary methods:

- `register(name, fn)`
- `get(name)`
- `list_names()`

Owner:

- Agent 1

#### `src/infra/jobs/runners.py`

Purpose:

- execution runner abstractions

Primary classes:

- `LocalScriptRunner`
- `AirflowRunnerStub`

Owner:

- Agent 1

#### `src/infra/jobs/scripts.py`

Purpose:

- built-in script implementations

Primary functions:

- `sync_all_balances_script()`
- `reconcile_recent_leaves_script()`
- `backfill_balances_script()`
- `repair_pending_reconciliation_script()`

Owner:

- Agent 2

## 5. Test Blueprint

### 5.1 Shared Test Support

#### `tests/conftest.py`

Purpose:

- shared fixture registration

Suggested fixtures:

- `settings`
- `db_engine`
- `db_session`
- `seed_service`
- `employee_user`
- `manager_user`
- `admin_user`
- `test_app`
- `test_client`

Owner:

- Agent 3

#### `tests/helpers/app_factory.py`

Purpose:

- create test app instances with optional dependency overrides

Primary functions:

- `build_test_app()`
- `build_test_client()`

Owner:

- Agent 3

#### `tests/helpers/auth.py`

Purpose:

- auth test helpers

Primary functions:

- `make_auth_header(user_id)`
- `make_employee_user()`
- `make_manager_user()`
- `make_admin_user()`

Owner:

- Agent 3

#### `tests/helpers/db.py`

Purpose:

- test DB lifecycle helpers

Primary functions:

- `create_test_db()`
- `reset_test_db()`
- `seed_test_db()`

Owner:

- Agent 1

#### `tests/helpers/fixtures.py`

Purpose:

- payload and model fixture builders

Primary functions:

- `build_leave_create_payload()`
- `build_leave_update_payload()`
- `build_balance_row()`

Owner:

- Agent 3

#### `tests/helpers/mock_hcm.py`

Purpose:

- mock HCM state helpers

Primary functions:

- `set_mock_hcm_scenario()`
- `seed_mock_hcm_balances()`
- `seed_mock_hcm_leave()`

Owner:

- Agent 3

#### `tests/helpers/overrides.py`

Purpose:

- dependency override helpers for FastAPI tests

Primary functions:

- `override_logged_in_user()`
- `override_hcm_service()`
- `clear_dependency_overrides()`

Owner:

- Agent 3

#### `tests/helpers/clocks.py`

Purpose:

- deterministic time helpers

Primary functions:

- `fixed_now()`
- `advance_time()`

Owner:

- Agent 3

### 5.2 Unit Tests

#### `tests/unit/test_auth_dependencies.py`

Primary test names:

- `test_missing_bearer_token_returns_401`
- `test_invalid_token_returns_401`
- `test_employee_dependency_accepts_employee`
- `test_manager_dependency_rejects_employee`
- `test_admin_dependency_rejects_manager`

Owner:

- Agent 3

#### `tests/unit/test_logged_in_user.py`

Primary test names:

- `test_is_employee_returns_true_only_for_employee`
- `test_is_manager_returns_true_only_for_manager`
- `test_is_admin_returns_true_only_for_admin`

Owner:

- Agent 2

#### `tests/unit/test_leave_state_machine.py`

Primary test names:

- `test_created_to_requested_transition_is_allowed`
- `test_requested_to_approved_transition_is_allowed`
- `test_requested_to_denied_transition_is_allowed`
- `test_invalid_transition_raises_error`
- `test_pending_reconciliation_can_resolve_to_final_state`

Owner:

- Agent 2

#### `tests/unit/test_leave_policy_service.py`

Primary test names:

- `test_employee_cannot_request_leave_for_another_user`
- `test_manager_can_approve_direct_report`
- `test_manager_cannot_approve_unrelated_employee`
- `test_admin_override_is_allowed`
- `test_invalid_date_range_is_rejected`

Owner:

- Agent 2

#### `tests/unit/test_balances_service.py`

Primary test names:

- `test_get_user_balances_scopes_by_user_and_location`
- `test_upsert_balance_preserves_unique_scope`
- `test_reconcile_balances_applies_external_values`

Owner:

- Agent 2

#### `tests/unit/test_http_client.py`

Primary test names:

- `test_http_client_returns_successful_response`
- `test_http_client_retries_transient_failure`
- `test_http_client_does_not_retry_validation_error`
- `test_http_client_timeout_raises_typed_error`

Owner:

- Agent 1

#### `tests/unit/test_retry_policy.py`

Primary test names:

- `test_retry_policy_respects_max_attempts`
- `test_retry_policy_computes_exponential_delay`
- `test_retry_policy_applies_jitter`

Owner:

- Agent 1

#### `tests/unit/test_rate_limit_service.py`

Primary test names:

- `test_rate_limit_headers_update_cached_state`
- `test_acquire_ratelimit_succeeds_when_tokens_available`
- `test_acquire_ratelimit_fails_when_tokens_unavailable`

Owner:

- Agent 1

#### `tests/unit/test_cache_service.py`

Primary test names:

- `test_cache_key_round_trip`
- `test_cache_namespace_isolation`
- `test_cache_ttl_expiration`
- `test_cache_delete_removes_key`

Owner:

- Agent 1

#### `tests/unit/test_mock_hcm_adapter.py`

Primary test names:

- `test_mock_hcm_adapter_returns_balances`
- `test_mock_hcm_adapter_creates_leave`
- `test_mock_hcm_adapter_returns_reconciliation_needed_for_ambiguous_result`

Owner:

- Agent 2

#### `tests/unit/test_scripts_service.py`

Primary test names:

- `test_run_script_creates_script_run_record`
- `test_unknown_script_name_raises_error`
- `test_cancel_run_marks_cancellation_requested`

Owner:

- Agent 2

#### `tests/unit/test_reconciliation_service.py`

Primary test names:

- `test_reconcile_leave_request_repairs_pending_record`
- `test_sync_all_balances_updates_local_state`

Owner:

- Agent 2

### 5.3 Integration Tests

#### `tests/integration/test_users_repository.py`

Primary test names:

- `test_users_repository_returns_reporting_tree`
- `test_users_repository_returns_direct_reports`

Owner:

- Agent 1

#### `tests/integration/test_leave_requests_repository.py`

Primary test names:

- `test_leave_requests_repository_creates_record`
- `test_leave_requests_repository_filters_by_manager_scope`
- `test_leave_requests_repository_detects_version_conflict`

Owner:

- Agent 1

#### `tests/integration/test_leave_balances_repository.py`

Primary test names:

- `test_leave_balances_repository_bulk_upsert_updates_existing_rows`
- `test_leave_balances_repository_enforces_unique_scope`

Owner:

- Agent 1

#### `tests/integration/test_hcm_configs_repository.py`

Primary test names:

- `test_hcm_configs_repository_returns_active_provider_config`

Owner:

- Agent 1

#### `tests/integration/test_script_runs_repository.py`

Primary test names:

- `test_script_runs_repository_marks_run_completed`
- `test_script_runs_repository_records_cancel_request`

Owner:

- Agent 1

#### `tests/integration/test_audit_events_repository.py`

Primary test names:

- `test_audit_events_repository_creates_event`
- `test_audit_events_repository_lists_events_by_actor`

Owner:

- Agent 1

#### `tests/integration/test_leaves_service_integration.py`

Primary test names:

- `test_leaves_service_persists_request_and_audit_event`
- `test_leaves_service_approves_valid_request`
- `test_leaves_service_detects_version_conflict`

Owner:

- Agent 2

#### `tests/integration/test_balances_service_integration.py`

Primary test names:

- `test_balances_service_reads_local_balances`
- `test_balances_service_bulk_reconcile_updates_rows`

Owner:

- Agent 2

#### `tests/integration/test_reconciliation_integration.py`

Primary test names:

- `test_reconciliation_service_repairs_pending_request_from_external_truth`
- `test_reconciliation_service_repairs_external_balance_drift`

Owner:

- Agent 2

#### `tests/integration/test_mock_hcm_adapter_integration.py`

Primary test names:

- `test_mock_hcm_adapter_integration_creates_leave_in_mock_store`
- `test_mock_hcm_adapter_integration_updates_leave_in_mock_store`

Owner:

- Agent 2

### 5.4 API Tests

#### `tests/api/test_health_routes.py`

Primary test names:

- `test_health_route_returns_ok`

Owner:

- Agent 3

#### `tests/api/test_leaves_employee_routes.py`

Primary test names:

- `test_employee_can_get_own_balances`
- `test_employee_can_get_own_current_leaves`
- `test_employee_can_submit_valid_leave_request`
- `test_employee_cannot_access_manager_queue`

Owner:

- Agent 3

#### `tests/api/test_leaves_manager_routes.py`

Primary test names:

- `test_manager_can_list_managed_leave_requests`
- `test_manager_can_approve_pending_request`
- `test_manager_cannot_approve_unrelated_employee_request`

Owner:

- Agent 3

#### `tests/api/test_leaves_admin_routes.py`

Primary test names:

- `test_admin_can_run_privileged_leave_update_if_supported`

Owner:

- Agent 3

#### `tests/api/test_scripts_routes.py`

Primary test names:

- `test_admin_can_run_script`
- `test_non_admin_cannot_run_script`
- `test_admin_can_query_script_status`
- `test_admin_can_request_script_cancellation`

Owner:

- Agent 3

#### `tests/api/test_mock_hcm_routes.py`

Primary test names:

- `test_mock_hcm_balance_route_returns_seeded_data`
- `test_mock_hcm_scenario_activation_changes_behavior`

Owner:

- Agent 3

### 5.5 End-to-End Tests

#### `tests/e2e/test_employee_request_happy_path.py`

Primary test names:

- `test_employee_request_happy_path`

Owner:

- Agent 3

#### `tests/e2e/test_employee_request_insufficient_balance.py`

Primary test names:

- `test_employee_request_insufficient_balance`

Owner:

- Agent 3

#### `tests/e2e/test_external_balance_refresh.py`

Primary test names:

- `test_external_balance_refresh_reconciles_local_store`

Owner:

- Agent 3

#### `tests/e2e/test_manager_approval_flow.py`

Primary test names:

- `test_manager_approval_flow`

Owner:

- Agent 3

#### `tests/e2e/test_manager_denial_flow.py`

Primary test names:

- `test_manager_denial_flow`

Owner:

- Agent 3

#### `tests/e2e/test_employee_cancel_flow.py`

Primary test names:

- `test_employee_cancel_flow`

Owner:

- Agent 3

#### `tests/e2e/test_cancel_vs_approve_race.py`

Primary test names:

- `test_cancel_vs_approve_race_resolves_without_silent_overwrite`

Owner:

- Agent 3

#### `tests/e2e/test_ambiguous_hcm_response.py`

Primary test names:

- `test_ambiguous_hcm_response_moves_request_to_pending_reconciliation`

Owner:

- Agent 3

#### `tests/e2e/test_rate_limit_retry_flow.py`

Primary test names:

- `test_rate_limit_retry_flow`

Owner:

- Agent 3

#### `tests/e2e/test_scheduled_sync_all_balances.py`

Primary test names:

- `test_scheduled_sync_all_balances`

Owner:

- Agent 3

#### `tests/e2e/test_repair_pending_reconciliation.py`

Primary test names:

- `test_repair_pending_reconciliation`

Owner:

- Agent 3

## 6. Build and Documentation Files

### `scripts/seed_local_db.py`

Purpose:

- run local seed flow from command line

Owner:

- Agent 1

### `scripts/reset_local_db.py`

Purpose:

- reset local SQLite DB for development or testing

Owner:

- Agent 1

### `scripts/export_docs.sh`

Purpose:

- export Markdown docs to PDF

Owner:

- Agent 3

### `pyproject.toml`

Purpose:

- dependency and tool configuration

Owner:

- Agent 1

### `README.md`

Purpose:

- project overview
- local development instructions
- test commands
- docs export commands

Owner:

- Agent 3

### `Makefile`

Purpose:

- common developer commands

Suggested targets:

- `install`
- `run`
- `seed`
- `test`
- `test-unit`
- `test-integration`
- `test-api`
- `test-e2e`
- `export-docs`

Owner:

- Agent 3

## 7. Handoff Contracts

### Agent 1 to Agent 2

Agent 1 must stabilize:

- ORM models
- DB session utilities
- repository constructor signatures
- repository method names
- cache interfaces
- HTTP client interface
- scheduler and registry interfaces

### Agent 2 to Agent 3

Agent 2 must stabilize:

- `LoggedInUser`
- domain enums
- service constructor signatures
- service public method names
- canonical HCM models
- script names
- command model shapes

### Agent 1 and Agent 2 to Agent 3

Both must avoid interface churn after API schemas and tests begin.

## 8. Suggested Development Order

1. Agent 1 completes bootstrap, DB, repositories, cache, HTTP client, scheduler base
2. Agent 2 completes domain, services, adapters, and script logic
3. Agent 3 completes auth wiring, routes, schemas, API tests, and end-to-end tests
4. All agents participate only in final bug-fix and polish passes after interfaces stabilize

## 9. Blueprint Completion Checklist

- every required document has a target file
- every application layer has a bounded package
- every major file has a named owner
- all route files map to API spec sections
- all repository files map to data model entities
- all service files map to business capabilities
- all test files map to documented scenarios
- all ownership notes align with the 3-agent implementation plan