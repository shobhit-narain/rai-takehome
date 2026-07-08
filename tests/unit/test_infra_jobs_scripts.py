# Tests for infrastructure job scripts.
# Validates that script functions delegate to the appropriate service methods.

from __future__ import annotations

from unittest.mock import MagicMock

from src.infra.jobs.scripts import (
    reconcile_recent_leaves_script,
    repair_pending_reconciliation_script,
)


# reconcile_recent_leaves_script calls service.reconcile_recent_leaves()
def test_reconcile_recent_leaves_script_delegates() -> None:
    service = MagicMock()
    reconcile_recent_leaves_script(service)
    service.reconcile_recent_leaves.assert_called_once()


# repair_pending_reconciliation_script calls service.repair_pending_reconciliation()
def test_repair_pending_reconciliation_script_delegates() -> None:
    service = MagicMock()
    repair_pending_reconciliation_script(service)
    service.repair_pending_reconciliation.assert_called_once()
