from __future__ import annotations

from pathlib import Path

from src.adapters.hcm.mock_hcm_adapter import MockHcmAdapter
from src.domain.leave_state_machine import LeaveStateMachine
from src.infra.db.factories import build_leave_request_record, build_user_record
from src.repositories.audit_events_repository import AuditEventsRepository
from src.repositories.leave_balances_repository import LeaveBalancesRepository
from src.repositories.leave_requests_repository import LeaveRequestsRepository
from src.repositories.users_repository import UsersRepository
from src.services.audit_service import AuditService
from src.services.reconciliation_service import ReconciliationService
from tests.helpers.mock_hcm import build_mock_hcm_state, write_mock_hcm_state


def _build_service(db_session, tmp_path: Path) -> ReconciliationService:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json", build_mock_hcm_state())
    hcm_adapter = MockHcmAdapter(state_file=state_file)
    return ReconciliationService(
        leave_requests_repository=LeaveRequestsRepository(db_session),
        leave_balances_repository=LeaveBalancesRepository(db_session),
        users_repository=UsersRepository(db_session),
        hcm_service=hcm_adapter,
        state_machine=LeaveStateMachine(),
        audit_service=AuditService(AuditEventsRepository(db_session)),
    )


def test_reconciliation_service_repairs_pending_request_from_external_truth(
    db_session, tmp_path: Path
) -> None:
    db_session.add(build_user_record(id="user_emp_00001"))
    db_session.flush()
    record = build_leave_request_record(
        id="leave-1",
        requestor_id="user_emp_00001",
        external_hcm_id="hcm_leave_0000001",
        status="pending_reconciliation",
    )
    db_session.add(record)
    db_session.flush()

    service = _build_service(db_session, tmp_path)
    updated = service.reconcile_leave_request("leave-1")

    assert updated.status in {"approved", "denied", "canceled", "complete", "requested"}


def test_reconciliation_service_repairs_external_balance_drift(db_session, tmp_path: Path) -> None:
    db_session.add(build_user_record(id="user_emp_00001"))
    db_session.flush()

    service = _build_service(db_session, tmp_path)
    updated = service.sync_all_balances()

    assert len(updated) == 2
