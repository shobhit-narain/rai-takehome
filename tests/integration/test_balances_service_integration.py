from __future__ import annotations

from src.infra.db.factories import build_leave_balance_record, build_user_record
from src.repositories.leave_balances_repository import LeaveBalancesRepository
from src.services.balances_service import BalancesService


def test_balances_service_reads_local_balances(db_session) -> None:
    db_session.add(build_user_record(id="emp-1"))
    db_session.flush()

    service = BalancesService(LeaveBalancesRepository(db_session))
    service.upsert_balance(build_leave_balance_record(id="bal-1", user_id="emp-1"))

    rows = service.get_user_balances("emp-1")
    assert len(rows) == 1


def test_balances_service_bulk_reconcile_updates_rows(db_session) -> None:
    db_session.add(build_user_record(id="emp-1"))
    db_session.flush()

    service = BalancesService(LeaveBalancesRepository(db_session))
    service.upsert_balance(
        build_leave_balance_record(id="bal-1", user_id="emp-1", leave_type="pto", num_available=5.0)
    )

    service.reconcile_balances(
        [build_leave_balance_record(id="bal-2", user_id="emp-1", leave_type="pto", num_available=3.0)]
    )

    rows = service.get_user_balances("emp-1")
    assert len(rows) == 1
    assert rows[0].num_available == 3.0
