# Tests for LeavePolicyService domain logic.
# Validates authorization rules for leave requests and updates across employee, manager, and admin roles.

from __future__ import annotations

from datetime import date

import pytest

from src.auth.current_user import LoggedInUser
from src.domain.enums import LeaveAction, LeaveStatus, LeaveType, UserRole
from src.domain.errors import PolicyViolationError
from src.domain.leave_policy import LeavePolicyService
from src.domain.models import LeaveCreateCommand, LeaveUpdateCommand


def _command(**overrides: object) -> LeaveCreateCommand:
    defaults: dict[str, object] = dict(
        leave_type=LeaveType.PTO,
        leave_duration=1.0,
        leave_start=date(2026, 8, 10),
        leave_end=date(2026, 8, 11),
        location_id="loc-1",
    )
    defaults.update(overrides)
    return LeaveCreateCommand(**defaults)


class _LeaveRequestStub:
    def __init__(self, requestor_id: str, status: str = LeaveStatus.REQUESTED.value) -> None:
        self.requestor_id = requestor_id
        self.status = status


# Employee cannot request leave for another employee (self-only rule)
def test_employee_cannot_request_leave_for_another_user() -> None:
    policy = LeavePolicyService()
    actor = LoggedInUser(user_id="emp-1", role=UserRole.EMPLOYEE, manager_id="mgr-1", location_id="loc-1")

    with pytest.raises(PolicyViolationError):
        policy.validate_leave_request(actor, "emp-2", _command())


# Manager can approve leave for direct report
def test_manager_can_approve_direct_report() -> None:
    policy = LeavePolicyService()
    actor = LoggedInUser(user_id="mgr-1", role=UserRole.MANAGER, manager_id=None, location_id="loc-1")
    leave_request = _LeaveRequestStub(requestor_id="emp-1")

    policy.validate_leave_update(actor, leave_request, LeaveAction.APPROVE, ["emp-1"])


# Manager cannot approve leave for employee outside their reporting tree
def test_manager_cannot_approve_unrelated_employee() -> None:
    policy = LeavePolicyService()
    actor = LoggedInUser(user_id="mgr-1", role=UserRole.MANAGER, manager_id=None, location_id="loc-1")
    leave_request = _LeaveRequestStub(requestor_id="emp-2")

    with pytest.raises(PolicyViolationError):
        policy.validate_leave_update(actor, leave_request, LeaveAction.APPROVE, ["emp-1"])


# Admin can override and approve any leave request regardless of reporting structure
def test_admin_override_is_allowed() -> None:
    policy = LeavePolicyService()
    actor = LoggedInUser(user_id="admin-1", role=UserRole.ADMIN, manager_id=None, location_id="loc-1")
    leave_request = _LeaveRequestStub(requestor_id="emp-2")

    policy.validate_leave_update(actor, leave_request, LeaveAction.APPROVE, [])


# Leave request with end date before start date is rejected
def test_invalid_date_range_is_rejected() -> None:
    policy = LeavePolicyService()
    actor = LoggedInUser(user_id="emp-1", role=UserRole.EMPLOYEE, manager_id="mgr-1", location_id="loc-1")

    with pytest.raises(PolicyViolationError):
        policy.validate_leave_request(
            actor, "emp-1", _command(leave_start=date(2026, 8, 11), leave_end=date(2026, 8, 10))
        )


# Manager cannot deny already-approved leave without mitigating circumstances
def test_manager_cannot_deny_approved_leave_without_mitigating_circumstances() -> None:
    policy = LeavePolicyService()
    actor = LoggedInUser(user_id="mgr-1", role=UserRole.MANAGER, manager_id=None, location_id="loc-1")
    leave_request = _LeaveRequestStub(requestor_id="emp-1", status=LeaveStatus.APPROVED.value)

    with pytest.raises(PolicyViolationError, match="mitigating_circumstances is required"):
        policy.validate_leave_update(
            actor, leave_request, LeaveAction.DENY, ["emp-1"], 
            LeaveUpdateCommand(action=LeaveAction.DENY)
        )


# Manager can deny approved leave when mitigating circumstances are provided
def test_manager_can_deny_approved_leave_with_mitigating_circumstances() -> None:
    policy = LeavePolicyService()
    actor = LoggedInUser(user_id="mgr-1", role=UserRole.MANAGER, manager_id=None, location_id="loc-1")
    leave_request = _LeaveRequestStub(requestor_id="emp-1", status=LeaveStatus.APPROVED.value)

    policy.validate_leave_update(
        actor, leave_request, LeaveAction.DENY, ["emp-1"],
        LeaveUpdateCommand(action=LeaveAction.DENY, mitigating_circumstances="Business needs changed")
    )


# Manager can deny requested (not yet approved) leave without mitigating circumstances
def test_manager_can_deny_requested_leave_without_mitigating_circumstances() -> None:
    policy = LeavePolicyService()
    actor = LoggedInUser(user_id="mgr-1", role=UserRole.MANAGER, manager_id=None, location_id="loc-1")
    leave_request = _LeaveRequestStub(requestor_id="emp-1", status=LeaveStatus.REQUESTED.value)

    # This should work without mitigating_circumstances since the status is REQUESTED, not APPROVED
    policy.validate_leave_update(
        actor, leave_request, LeaveAction.DENY, ["emp-1"],
        LeaveUpdateCommand(action=LeaveAction.DENY)
    )
