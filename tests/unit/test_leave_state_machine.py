# Tests for the LeaveStateMachine domain logic.
# Validates all valid state transitions, invalid transition rejection, and reconciliation resolution.

from __future__ import annotations

import pytest

from src.domain.enums import LeaveAction, LeaveStatus
from src.domain.errors import InvalidStateTransitionError
from src.domain.leave_state_machine import LeaveStateMachine


# Created -> Requested transition is valid (employee submits leave request)
def test_created_to_requested_transition_is_allowed() -> None:
    machine = LeaveStateMachine()
    assert machine.next_status(LeaveStatus.CREATED, LeaveAction.SUBMIT) == LeaveStatus.REQUESTED


# Requested -> Approved transition is valid (manager approves request)
def test_requested_to_approved_transition_is_allowed() -> None:
    machine = LeaveStateMachine()
    assert machine.next_status(LeaveStatus.REQUESTED, LeaveAction.APPROVE) == LeaveStatus.APPROVED


# Requested -> Denied transition is valid (manager denies request)
def test_requested_to_denied_transition_is_allowed() -> None:
    machine = LeaveStateMachine()
    assert machine.next_status(LeaveStatus.REQUESTED, LeaveAction.DENY) == LeaveStatus.DENIED


# Invalid transition (e.g., DENIED -> APPROVE) raises domain error
def test_invalid_transition_raises_error() -> None:
    machine = LeaveStateMachine()
    with pytest.raises(InvalidStateTransitionError):
        machine.next_status(LeaveStatus.DENIED, LeaveAction.APPROVE)


# Pending reconciliation can resolve to final approved state
def test_pending_reconciliation_can_resolve_to_final_state() -> None:
    machine = LeaveStateMachine()
    assert machine.resolve_reconciliation(LeaveStatus.APPROVED) == LeaveStatus.APPROVED


# Approved -> Denied transition is valid (with mitigating circumstances)
def test_approved_to_denied_transition_is_allowed() -> None:
    machine = LeaveStateMachine()
    assert machine.next_status(LeaveStatus.APPROVED, LeaveAction.DENY) == LeaveStatus.DENIED
