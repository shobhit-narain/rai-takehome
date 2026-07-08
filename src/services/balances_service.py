from __future__ import annotations

from src.infra.db.models import LeaveBalanceRecord
from src.repositories.leave_balances_repository import LeaveBalancesRepository


class BalancesService:
    def __init__(self, leave_balances_repository: LeaveBalancesRepository) -> None:
        self.leave_balances_repository = leave_balances_repository

    def get_user_balances(
        self, user_id: str, location_id: str | None = None
    ) -> list[LeaveBalanceRecord]:
        return self.leave_balances_repository.list_for_user(user_id, location_id)

    def upsert_balance(self, balance_model: LeaveBalanceRecord) -> LeaveBalanceRecord:
        return self.leave_balances_repository.upsert(balance_model)

    def bulk_upsert_balances(
        self, balance_models: list[LeaveBalanceRecord]
    ) -> list[LeaveBalanceRecord]:
        return self.leave_balances_repository.bulk_upsert(balance_models)

    def reconcile_balances(
        self, external_balances: list[LeaveBalanceRecord]
    ) -> list[LeaveBalanceRecord]:
        return self.bulk_upsert_balances(external_balances)
