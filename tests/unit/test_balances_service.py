from __future__ import annotations

from unittest.mock import MagicMock

from src.services.balances_service import BalancesService


def test_get_user_balances_scopes_by_user_and_location() -> None:
    repo = MagicMock()
    service = BalancesService(repo)

    service.get_user_balances("emp-1", location_id="loc-1")

    repo.list_for_user.assert_called_once_with("emp-1", "loc-1")


def test_upsert_balance_preserves_unique_scope() -> None:
    repo = MagicMock()
    service = BalancesService(repo)
    balance = object()

    service.upsert_balance(balance)

    repo.upsert.assert_called_once_with(balance)


def test_reconcile_balances_applies_external_values() -> None:
    repo = MagicMock()
    service = BalancesService(repo)
    balances = [object(), object()]

    service.reconcile_balances(balances)

    repo.bulk_upsert.assert_called_once_with(balances)
