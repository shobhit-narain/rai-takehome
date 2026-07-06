from __future__ import annotations

from datetime import datetime, timezone

from src.adapters.hcm.mapper import HcmMapper
from src.adapters.hcm.port import HcmServicePort
from src.domain.enums import LeaveStatus
from src.domain.leave_state_machine import LeaveStateMachine
from src.infra.db.models import LeaveBalanceRecord, LeaveRequestRecord
from src.repositories.leave_balances_repository import LeaveBalancesRepository
from src.repositories.leave_requests_repository import LeaveRequestsRepository
from src.repositories.users_repository import UsersRepository
from src.services.audit_service import AuditService


class ReconciliationService:
    def __init__(
        self,
        leave_requests_repository: LeaveRequestsRepository,
        leave_balances_repository: LeaveBalancesRepository,
        users_repository: UsersRepository,
        hcm_service: HcmServicePort,
        state_machine: LeaveStateMachine,
        audit_service: AuditService,
        hcm_mapper: HcmMapper | None = None,
    ) -> None:
        self.leave_requests_repository = leave_requests_repository
        self.leave_balances_repository = leave_balances_repository
        self.users_repository = users_repository
        self.hcm_service = hcm_service
        self.state_machine = state_machine
        self.audit_service = audit_service
        self.hcm_mapper = hcm_mapper or HcmMapper()

    def reconcile_leave_request(self, leave_id: str) -> LeaveRequestRecord:
        record = self.leave_requests_repository.get_by_id(leave_id)
        if record is None:
            raise ValueError(f"leave request {leave_id} not found")
        if not record.external_hcm_id:
            return record

        raw = self.hcm_service.update_leave(record.external_hcm_id, "request_change")
        result = self.hcm_mapper.to_canonical_leave_result(raw)
        target_status = self._map_external_status(result.status)
        if target_status is not None and self.state_machine.can_resolve_reconciliation(target_status):
            record.status = self.state_machine.resolve_reconciliation(target_status).value
            record.failure_reason = result.failure_reason
            record.updated_ts = datetime.now(timezone.utc)
            record.last_synced_ts = record.updated_ts
            self.leave_requests_repository.update(record)
            self.audit_service.record_reconciliation("system", record.id, {"status": record.status})
        return record

    def reconcile_recent_leaves(self) -> list[LeaveRequestRecord]:
        pending = self.leave_requests_repository.list_by_status(
            LeaveStatus.PENDING_RECONCILIATION.value
        )
        return [self.reconcile_leave_request(record.id) for record in pending]

    def sync_all_balances(self) -> list[LeaveBalanceRecord]:
        updated: list[LeaveBalanceRecord] = []
        for user in self.users_repository.list_all():
            for raw_balance in self.hcm_service.get_balances(user.id):
                balance = LeaveBalanceRecord(
                    id=f"{user.id}:{raw_balance['location_id']}:{raw_balance['leave_type']}",
                    user_id=user.id,
                    location_id=raw_balance["location_id"],
                    leave_type=raw_balance["leave_type"],
                    num_available=float(raw_balance["num_available"]),
                    num_ytd_taken=float(raw_balance["num_ytd_taken"]),
                    num_limit=float(raw_balance["num_limit"]),
                    external_updated_ts=(
                        datetime.fromisoformat(raw_balance["external_updated_ts"])
                        if raw_balance.get("external_updated_ts")
                        else None
                    ),
                    updated_ts=datetime.now(timezone.utc),
                )
                updated.append(self.leave_balances_repository.upsert(balance))
        return updated

    def repair_pending_reconciliation(self) -> list[LeaveRequestRecord]:
        return self.reconcile_recent_leaves()

    def _map_external_status(self, status: str) -> LeaveStatus | None:
        try:
            return LeaveStatus(status)
        except ValueError:
            return None
