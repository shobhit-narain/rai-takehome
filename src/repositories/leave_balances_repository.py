from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infra.db.models import LeaveBalanceRecord


class LeaveBalancesRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_user(
        self, user_id: str, location_id: str | None = None
    ) -> list[LeaveBalanceRecord]:
        stmt = select(LeaveBalanceRecord).where(LeaveBalanceRecord.user_id == user_id)
        if location_id is not None:
            stmt = stmt.where(LeaveBalanceRecord.location_id == location_id)
        return list(self.session.scalars(stmt).all())

    def upsert(self, balance_model: LeaveBalanceRecord) -> LeaveBalanceRecord:
        stmt = select(LeaveBalanceRecord).where(
            LeaveBalanceRecord.user_id == balance_model.user_id,
            LeaveBalanceRecord.location_id == balance_model.location_id,
            LeaveBalanceRecord.leave_type == balance_model.leave_type,
        )
        existing = self.session.scalars(stmt).first()
        if existing is None:
            self.session.add(balance_model)
            self.session.flush()
            return balance_model

        existing.num_available = balance_model.num_available
        existing.num_ytd_taken = balance_model.num_ytd_taken
        existing.num_limit = balance_model.num_limit
        existing.external_updated_ts = balance_model.external_updated_ts
        existing.updated_ts = balance_model.updated_ts
        self.session.flush()
        return existing

    def bulk_upsert(
        self, balance_models: list[LeaveBalanceRecord]
    ) -> list[LeaveBalanceRecord]:
        return [self.upsert(model) for model in balance_models]
