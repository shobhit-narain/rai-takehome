# API Specification

## 1. Document Scope

This document defines the external HTTP API for the Time-Off Microservice.

It covers:

- authentication model
- error envelope
- leave endpoints
- script endpoints
- mock HCM endpoints
- request and response schemas
- filtering and pagination behavior

This API is intended for internal product use, automated tests, and mock integration flows.

## 2. Conventions

### Base URL

```text
/api/v1
```

### Content Type

Requests and responses use:

```text
application/json
```

### Authentication

Protected endpoints require a bearer token:

```text
Authorization: Bearer <token>
```

For the initial implementation, tokens may resolve to seeded local users.

### Time Format

All timestamps must be ISO 8601 strings in UTC.

Example:

```json
"2026-07-05T22:15:00Z"
```

### Identifiers

All IDs are strings at the API boundary.

### Error Behavior

All non-success responses must use the standard error envelope defined below.

## 3. Error Envelope

### Shape

```json
{
  "code": "STRING_CODE",
  "message": "Human readable message",
  "details": {},
  "request_id": "req_12345"
}
```

### Standard Error Codes

- `AUTH_REQUIRED`
- `ACCESS_DENIED`
- `VALIDATION_ERROR`
- `INVALID_STATE_TRANSITION`
- `INSUFFICIENT_BALANCE`
- `RESOURCE_NOT_FOUND`
- `CONFLICT`
- `UPSTREAM_TIMEOUT`
- `UPSTREAM_RATE_LIMITED`
- `UPSTREAM_VALIDATION_ERROR`
- `RECONCILIATION_REQUIRED`
- `INTERNAL_ERROR`

### Example

```json
{
  "code": "ACCESS_DENIED",
  "message": "Manager cannot update leave requests outside the reporting tree",
  "details": {
    "leave_id": "leave_10042"
  },
  "request_id": "req_b2f80e8d"
}
```

## 4. Authentication Model

### Roles

Supported roles:

- `employee`
- `manager`
- `admin`

### Current User Context

The service resolves the authenticated user into a current-user object with:

- `user_id`
- `role`
- `manager_id`
- `location_id`

### Authorization Rules

- employees can access only their own leave data
- managers can access only data for employees in their reporting tree
- admins can access all leave and script routes
- script routes are admin-only by default

## 5. Common Schemas

### ErrorResponse

```json
{
  "code": "STRING_CODE",
  "message": "Human readable message",
  "details": {},
  "request_id": "req_12345"
}
```

### PaginationMeta

```json
{
  "page": 1,
  "page_size": 50,
  "total_items": 250,
  "total_pages": 5
}
```

### PagedResponse

```json
{
  "items": [],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_items": 250,
    "total_pages": 5
  }
}
```

## 6. Leave Domain Schemas

### LeaveBalance

```json
{
  "user_id": "user_1001",
  "location_id": "loc_us_ca",
  "leave_type": "pto",
  "num_available": 10.0,
  "num_ytd_taken": 4.0,
  "num_limit": 15.0,
  "external_updated_ts": "2026-07-01T00:00:00Z",
  "updated_ts": "2026-07-05T21:10:00Z"
}
```

### LeaveRequest

```json
{
  "id": "leave_10042",
  "external_hcm_id": "hcm_leave_555",
  "requestor_id": "user_1001",
  "approver_id": "user_2001",
  "location_id": "loc_us_ca",
  "leave_type": "pto",
  "leave_duration": 2.0,
  "leave_start": "2026-08-10",
  "leave_end": "2026-08-11",
  "status": "requested",
  "failure_reason": null,
  "version": 3,
  "created_ts": "2026-07-05T21:00:00Z",
  "updated_ts": "2026-07-05T21:05:00Z",
  "approved_ts": null,
  "complete_ts": null,
  "last_synced_ts": "2026-07-05T21:05:00Z"
}
```

### LeaveCreateRequest

```json
{
  "leave_type": "pto",
  "leave_duration": 2.0,
  "leave_start": "2026-08-10",
  "leave_end": "2026-08-11",
  "location_id": "loc_us_ca",
  "notes": "Family event"
}
```

### LeaveUpdateRequest

```json
{
  "action": "approve",
  "leave_duration": 2.0,
  "leave_start": "2026-08-10",
  "leave_end": "2026-08-11",
  "notes": "Approved"
}
```

### Supported Leave Actions

- `cancel`
- `modify`
- `approve`
- `deny`
- `request_change`
- `complete`

### Supported Leave Statuses

- `created`
- `requested`
- `approved`
- `denied`
- `complete`
- `canceled`
- `pending_reconciliation`

## 7. Employee Leave Endpoints

### GET /api/v1/leaves/balance

Returns leave balances for the authenticated user.

#### Authorization

- employee
- manager
- admin

Managers and admins calling this route receive balances for themselves unless an admin-only override route is added later.

#### Response 200

```json
{
  "items": [
    {
      "user_id": "user_1001",
      "location_id": "loc_us_ca",
      "leave_type": "pto",
      "num_available": 10.0,
      "num_ytd_taken": 4.0,
      "num_limit": 15.0,
      "external_updated_ts": "2026-07-01T00:00:00Z",
      "updated_ts": "2026-07-05T21:10:00Z"
    },
    {
      "user_id": "user_1001",
      "location_id": "loc_us_ca",
      "leave_type": "sick",
      "num_available": 5.0,
      "num_ytd_taken": 1.0,
      "num_limit": 8.0,
      "external_updated_ts": "2026-07-01T00:00:00Z",
      "updated_ts": "2026-07-05T21:10:00Z"
    }
  ]
}
```

#### Error Responses

- `401 AUTH_REQUIRED`
- `500 INTERNAL_ERROR`

### GET /api/v1/leaves/current

Returns current and recent leave requests for the authenticated user.

#### Query Parameters

- `status` optional, repeatable
- `limit` optional, default `50`
- `offset` optional, default `0`

#### Example Request

```text
GET /api/v1/leaves/current?status=requested&status=approved&limit=20&offset=0
```

#### Response 200

```json
{
  "items": [
    {
      "id": "leave_10042",
      "external_hcm_id": "hcm_leave_555",
      "requestor_id": "user_1001",
      "approver_id": "user_2001",
      "location_id": "loc_us_ca",
      "leave_type": "pto",
      "leave_duration": 2.0,
      "leave_start": "2026-08-10",
      "leave_end": "2026-08-11",
      "status": "requested",
      "failure_reason": null,
      "version": 3,
      "created_ts": "2026-07-05T21:00:00Z",
      "updated_ts": "2026-07-05T21:05:00Z",
      "approved_ts": null,
      "complete_ts": null,
      "last_synced_ts": "2026-07-05T21:05:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 1,
    "total_pages": 1
  }
}
```

#### Error Responses

- `401 AUTH_REQUIRED`
- `500 INTERNAL_ERROR`

### POST /api/v1/leaves/request

Creates a leave request for the authenticated user.

#### Authorization

- employee
- manager
