from __future__ import annotations

from src.domain.enums import LeaveAction, LeaveStatus
from src.domain.errors import InvalidStateTransitionError


class LeaveStateMachine:
    _TRANSITIONS: dict[tuple[LeaveStatus, LeaveAction], LeaveStatus] = {
        (LeaveStatus.CREATED, LeaveAction.SUBMIT): LeaveStatus.REQUESTED,
        (LeaveStatus.CREATED, LeaveAction.CANCEL): LeaveStatus.CANCELED,
        (LeaveStatus.REQUESTED, LeaveAction.APPROVE): LeaveStatus.APPROVED,
        (LeaveStatus.REQUESTED, LeaveAction.DENY): LeaveStatus.DENIED,
        (LeaveStatus.REQUESTED, LeaveAction.CANCEL): LeaveStatus.CANCELED,
        (LeaveStatus.REQUESTED, LeaveAction.MODIFY): LeaveStatus.REQUESTED,
        (LeaveStatus.REQUESTED, LeaveAction.REQUEST_CHANGE): LeaveStatus.REQUESTED,
        (LeaveStatus.APPROVED, LeaveAction.CANCEL): LeaveStatus.CANCELED,
        (LeaveStatus.APPROVED, LeaveAction.COMPLETE): LeaveStatus.COMPLETE,
        (LeaveStatus.APPROVED, LeaveAction.DENY): LeaveStatus.DENIED,
    }

    _RECONCILIATION_RESOLUTIONS = {
        LeaveStatus.APPROVED,
        LeaveStatus.DENIED,
        LeaveStatus.CANCELED,
        LeaveStatus.COMPLETE,
        LeaveStatus.REQUESTED,
    }

    def can_transition(self, current_status: LeaveStatus, action: LeaveAction) -> bool:
        return (current_status, action) in self._TRANSITIONS

    def next_status(self, current_status: LeaveStatus, action: LeaveAction) -> LeaveStatus:
        if not self.can_transition(current_status, action):
            raise InvalidStateTransitionError(
                f"cannot apply action {action.value} from status {current_status.value}"
            )
        return self._TRANSITIONS[(current_status, action)]

    def can_resolve_reconciliation(self, target_status: LeaveStatus) -> bool:
        return target_status in self._RECONCILIATION_RESOLUTIONS

    def resolve_reconciliation(self, target_status: LeaveStatus) -> LeaveStatus:
        if not self.can_resolve_reconciliation(target_status):
            raise InvalidStateTransitionError(
                f"pending_reconciliation cannot resolve to {target_status.value}"
            )
        return target_status
