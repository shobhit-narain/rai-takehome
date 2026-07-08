from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from src.adapters.hcm.mapper import HcmMapper
from src.adapters.hcm.port import HcmServicePort
from src.auth.current_user import LoggedInUser
from src.domain.enums import LeaveAction, LeaveStatus
from src.domain.errors import InsufficientBalanceError, ReconciliationRequiredError
from src.domain.leave_policy import LeavePolicyService
from src.domain.leave_state_machine import LeaveStateMachine
from src.domain.models import LeaveCreateCommand, LeaveUpdateCommand
from src.infra.db.models import LeaveRequestRecord
from src.repositories.leave_requests_repository import LeaveRequestsRepository
from src.services.audit_service import AuditService
from src.services.users_service import UsersService


class LeavesService:
    def __init__(
        self,
        leave_requests_repository: LeaveRequestsRepository,
        hcm_service: HcmServicePort,
        policy_service: LeavePolicyService,
        state_machine: LeaveStateMachine,
        audit_service: AuditService,
        users_service: UsersService,
        hcm_mapper: HcmMapper | None = None,
    ) -> None:
        self.leave_requests_repository = leave_requests_repository
        self.hcm_service = hcm_service
        self.policy_service = policy_service
        self.state_machine = state_machine
        self.audit_service = audit_service
        self.users_service = users_service
        self.hcm_mapper = hcm_mapper or HcmMapper()

    def get_current_leaves(
        self, actor: LoggedInUser, filters: dict[str, Any] | None = None
    ) -> list[LeaveRequestRecord]:
        return self.leave_requests_repository.list_by_requestor(actor.user_id, filters)

    def get_manager_leave_requests(
        self, actor: LoggedInUser, filters: dict[str, Any] | None = None
    ) -> list[LeaveRequestRecord]:
        reporting_tree = self.users_service.get_reporting_tree(actor.user_id)
        user_ids = [user.id for user in reporting_tree]
        return self.leave_requests_repository.list_for_manager_scope(user_ids, filters)

    def request_leave(self, actor: LoggedInUser, command: LeaveCreateCommand) -> LeaveRequestRecord:
        self.policy_service.validate_leave_request(actor, actor.user_id, command)

        now = datetime.now(UTC)
        record = LeaveRequestRecord(
            id=str(uuid.uuid4()),
            external_hcm_id=None,
            requestor_id=actor.user_id,
            approver_id=actor.manager_id,
            location_id=command.location_id,
            leave_type=command.leave_type.value,
            leave_duration=command.leave_duration,
            leave_start=command.leave_start,
            leave_end=command.leave_end,
            status=LeaveStatus.CREATED.value,
            failure_reason=None,
            version=1,
            created_ts=now,
            updated_ts=now,
        )
        self.leave_requests_repository.create(record)

        payload = {
            "user_id": actor.user_id,
            "location_id": command.location_id,
            "leave_type": command.leave_type.value,
            "leave_duration": command.leave_duration,
            "leave_start": command.leave_start.isoformat(),
            "leave_end": command.leave_end.isoformat(),
            "approver_id": actor.manager_id,
        }
        raw_result = self.hcm_service.create_leave(payload)
        result = self.hcm_mapper.to_canonical_leave_result(raw_result)

        if result.status == "rejected":
            record.status = LeaveStatus.DENIED.value
            record.failure_reason = result.failure_reason
            self.leave_requests_repository.update(record)
            raise InsufficientBalanceError(result.failure_reason or "leave request rejected")

        if result.status == "pending_reconciliation":
            record.status = LeaveStatus.PENDING_RECONCILIATION.value
            record.external_hcm_id = result.external_hcm_id
            record.failure_reason = result.failure_reason
            self.leave_requests_repository.update(record)
            self.audit_service.record_leave_created(actor, record)
            raise ReconciliationRequiredError(
                "upstream confirmation is ambiguous; reconciliation required"
            )

        record.status = self.state_machine.next_status(LeaveStatus.CREATED, LeaveAction.SUBMIT).value
        record.external_hcm_id = result.external_hcm_id
        record.last_synced_ts = now
        self.leave_requests_repository.update(record)
        self.audit_service.record_leave_created(actor, record)
        return record

    def update_leave_request(
        self, actor: LoggedInUser, leave_id: str, command: LeaveUpdateCommand
    ) -> LeaveRequestRecord:
        record = self.leave_requests_repository.get_by_id(leave_id)
        if record is None:
            raise ValueError(f"leave request {leave_id} not found")

        reporting_tree_ids = [
            user.id for user in self.users_service.get_reporting_tree(actor.user_id)
        ]
        self.policy_service.validate_leave_update(actor, record, command.action, reporting_tree_ids, command)

        current_status = LeaveStatus(record.status)
        next_status = self.state_machine.next_status(current_status, command.action)

        if record.external_hcm_id:
            self.hcm_service.update_leave(record.external_hcm_id, command.action.value)

        expected_version = record.version
        record.status = next_status.value
        record.updated_ts = datetime.now(UTC)
        if next_status == LeaveStatus.APPROVED:
            record.approved_ts = record.updated_ts
        if next_status == LeaveStatus.COMPLETE:
            record.complete_ts = record.updated_ts

        updated = self.leave_requests_repository.update_with_version_check(record, expected_version)
        self.audit_service.record_leave_updated(actor, updated, command.action.value)
        return updated
