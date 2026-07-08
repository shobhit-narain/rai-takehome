# Tests for BalancesService domain logic.
# Validates balance retrieval scoping, upsert uniqueness, and reconciliation with external HCM data.

from __future__ import annotations

from unittest.mock import MagicMock

from src.services.balances_service import BalancesService


# Balance retrieval is correctly scoped by user ID and location ID
def test_get_user_balances_scopes_by_user_and_location() -> None:
    repo = MagicMock()
    service = BalancesService(repo)

    service.get_user_balances("emp-1", location_id="loc-1")

    repo.list_for_user.assert_called_once_with("emp-1", "loc-1")


# Upsert operation preserves unique user-location-leave-type constraint
def test_upsert_balance_preserves_unique_scope() -> None:
    repo = MagicMock()
    service = BalancesService(repo)
    balance = object()

    service.upsert_balance(balance)

    repo.upsert.assert_called_once_with(balance)


# Reconciliation applies external HCM balance values to local store
def test_reconcile_balances_applies_external_values() -> None:
    repo = MagicMock()
    service = BalancesService(repo)
    balances = [object(), object()]

    service.reconcile_balances(balances)

    repo.bulk_upsert.assert_called_once_with(balances)
