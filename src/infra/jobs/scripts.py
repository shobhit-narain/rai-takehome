from __future__ import annotations

from src.infra.db.models import LeaveBalanceRecord, LeaveRequestRecord
from src.services.reconciliation_service import ReconciliationService


def sync_all_balances_script(
    reconciliation_service: ReconciliationService,
) -> list[LeaveBalanceRecord]:
    return reconciliation_service.sync_all_balances()


def reconcile_recent_leaves_script(
    reconciliation_service: ReconciliationService,
) -> list[LeaveRequestRecord]:
    return reconciliation_service.reconcile_recent_leaves()


def backfill_balances_script(
    reconciliation_service: ReconciliationService,
) -> list[LeaveBalanceRecord]:
    return reconciliation_service.sync_all_balances()


def repair_pending_reconciliation_script(
    reconciliation_service: ReconciliationService,
) -> list[LeaveRequestRecord]:
    return reconciliation_service.repair_pending_reconciliation()
