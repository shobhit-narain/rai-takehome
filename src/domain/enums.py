from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"


class LeaveType(str, Enum):
    PTO = "pto"
    SICK = "sick"
    UNPAID = "unpaid"


class LeaveStatus(str, Enum):
    CREATED = "created"
    REQUESTED = "requested"
    APPROVED = "approved"
    DENIED = "denied"
    COMPLETE = "complete"
    CANCELED = "canceled"
    PENDING_RECONCILIATION = "pending_reconciliation"


class LeaveAction(str, Enum):
    SUBMIT = "submit"
    CANCEL = "cancel"
    MODIFY = "modify"
    APPROVE = "approve"
    DENY = "deny"
    REQUEST_CHANGE = "request_change"
    COMPLETE = "complete"


class ScriptRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
