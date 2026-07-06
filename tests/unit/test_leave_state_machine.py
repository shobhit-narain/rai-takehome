from __future__ import annotations

import pytest

from src.domain.enums import LeaveAction, LeaveStatus
from src.domain.errors import InvalidStateTransitionError
from src.domain.leave_state_machine import LeaveStateMachine


def test_created_to_requested_transition_is_allowed() -> None:
    machine = LeaveStateMachine()
    assert machine.next_status(LeaveStatus.CREATED, LeaveAction.SUBMIT) == LeaveStatus.REQUESTED


def test_requested_to_approved_transition_is_allowed() -> None:
    machine = LeaveStateMachine()
    assert machine.next_status(LeaveStatus.REQUESTED, LeaveAction.APPROVE) == LeaveStatus.APPROVED


def test_requested_to_denied_transition_is_allowed() -> None:
    machine = LeaveStateMachine()
    assert machine.next_status(LeaveStatus.REQUESTED, LeaveAction.DENY) == LeaveStatus.DENIED


def test_invalid_transition_raises_error() -> None:
    machine = LeaveStateMachine()
    with pytest.raises(InvalidStateTransitionError):
        machine.next_status(LeaveStatus.DENIED, LeaveAction.APPROVE)


def test_pending_reconciliation_can_resolve_to_final_state() -> None:
    machine = LeaveStateMachine()
    assert machine.resolve_reconciliation(LeaveStatus.APPROVED) == LeaveStatus.APPROVED
