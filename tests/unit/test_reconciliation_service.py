from __future__ import annotations

from unittest.mock import MagicMock

from src.domain.leave_state_machine import LeaveStateMachine
from src.services.reconciliation_service import ReconciliationService


def _service(leave_requests_repo, hcm_service) -> ReconciliationService:
    return ReconciliationService(
        leave_requests_repository=leave_requests_repo,
        leave_balances_repository=MagicMock(),
        users_repository=MagicMock(),
        hcm_service=hcm_service,
        state_machine=LeaveStateMachine(),
        audit_service=MagicMock(),
    )


def test_reconcile_leave_request_repairs_pending_record() -> None:
    record = MagicMock(id="leave-1", external_hcm_id="hcm-1", status="pending_reconciliation")
    leave_requests_repo = MagicMock()
    leave_requests_repo.get_by_id.return_value = record

    hcm_service = MagicMock()
    hcm_service.update_leave.return_value = {
        "status": "approved",
        "external_hcm_id": "hcm-1",
        "failure_reason": "",
    }

    service = _service(leave_requests_repo, hcm_service)
    result = service.reconcile_leave_request("leave-1")

    assert result.status == "approved"
    leave_requests_repo.update.assert_called_once_with(record)


def test_reconcile_leave_request_returns_early_without_external_id() -> None:
    record = MagicMock(id="leave-1", external_hcm_id=None)
    leave_requests_repo = MagicMock()
    leave_requests_repo.get_by_id.return_value = record

    service = _service(leave_requests_repo, MagicMock())
    result = service.reconcile_leave_request("leave-1")

    assert result is record
    leave_requests_repo.update.assert_not_called()


def test_reconcile_leave_request_ignores_unresolvable_status() -> None:
    record = MagicMock(id="leave-1", external_hcm_id="hcm-1", status="pending_reconciliation")
    leave_requests_repo = MagicMock()
    leave_requests_repo.get_by_id.return_value = record

    hcm_service = MagicMock()
    hcm_service.update_leave.return_value = {"status": "not_a_real_status"}

    service = _service(leave_requests_repo, hcm_service)
    result = service.reconcile_leave_request("leave-1")

    assert result is record
    leave_requests_repo.update.assert_not_called()


def test_sync_all_balances_updates_local_state() -> None:
    user = MagicMock(id="emp-1")
    leave_requests_repo = MagicMock()
    hcm_service = MagicMock()
    hcm_service.get_balances.return_value = [
        {
            "location_id": "loc-1",
            "leave_type": "pto",
            "num_available": 5.0,
            "num_ytd_taken": 1.0,
            "num_limit": 10.0,
            "external_updated_ts": None,
        }
    ]

    service = _service(leave_requests_repo, hcm_service)
    service.users_repository.list_all.return_value = [user]

    updated = service.sync_all_balances()

    assert len(updated) == 1
    service.leave_balances_repository.upsert.assert_called_once()
