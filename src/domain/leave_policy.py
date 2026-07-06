from __future__ import annotations

from typing import Any

from src.auth.current_user import LoggedInUser
from src.domain.enums import LeaveAction
from src.domain.errors import PolicyViolationError
from src.domain.models import LeaveCreateCommand


class LeavePolicyService:
    def validate_leave_request(
        self, actor: LoggedInUser, target_user_id: str, request: LeaveCreateCommand
    ) -> None:
        if not actor.is_admin() and actor.user_id != target_user_id:
            raise PolicyViolationError("employees may only request leave for themselves")
        if request.leave_end < request.leave_start:
            raise PolicyViolationError("leave_end must not be before leave_start")

    def validate_leave_update(
        self,
        actor: LoggedInUser,
        leave_request: Any,
        action: LeaveAction,
        reporting_tree_user_ids: list[str],
    ) -> None:
        if actor.is_admin():
            return
        if actor.user_id == leave_request.requestor_id:
            return
        if actor.is_manager() and leave_request.requestor_id in reporting_tree_user_ids:
            return
        raise PolicyViolationError("actor is not permitted to update this leave request")
