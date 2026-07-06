from __future__ import annotations

from unittest.mock import MagicMock

from src.infra.jobs.scripts import (
    reconcile_recent_leaves_script,
    repair_pending_reconciliation_script,
)


def test_reconcile_recent_leaves_script_delegates() -> None:
    service = MagicMock()
    reconcile_recent_leaves_script(service)
    service.reconcile_recent_leaves.assert_called_once()


def test_repair_pending_reconciliation_script_delegates() -> None:
    service = MagicMock()
    repair_pending_reconciliation_script(service)
    service.repair_pending_reconciliation.assert_called_once()
