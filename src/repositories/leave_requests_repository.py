from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from src.infra.db.models import LeaveRequestRecord


class ConflictVersionError(Exception):
    def __init__(self, leave_id: str, expected_version: int, actual_version: int) -> None:
        super().__init__(
            f"version conflict for leave request {leave_id}: "
            f"expected {expected_version}, got {actual_version}"
        )
        self.leave_id = leave_id
        self.expected_version = expected_version
        self.actual_version = actual_version


class LeaveRequestsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, leave_id: str) -> LeaveRequestRecord | None:
        return self.session.get(LeaveRequestRecord, leave_id)

    def list_by_status(self, status: str) -> list[LeaveRequestRecord]:
        stmt = select(LeaveRequestRecord).where(LeaveRequestRecord.status == status)
        return list(self.session.scalars(stmt).all())

    def list_by_requestor(
        self, user_id: str, filters: dict[str, object] | None = None
    ) -> list[LeaveRequestRecord]:
        stmt = select(LeaveRequestRecord).where(LeaveRequestRecord.requestor_id == user_id)
        stmt = self._apply_filters(stmt, filters)
        return list(self.session.scalars(stmt).all())

    def list_for_manager_scope(
        self, user_ids: list[str], filters: dict[str, object] | None = None
    ) -> list[LeaveRequestRecord]:
        stmt = select(LeaveRequestRecord).where(LeaveRequestRecord.requestor_id.in_(user_ids))
        stmt = self._apply_filters(stmt, filters)
        return list(self.session.scalars(stmt).all())

    def create(self, model: LeaveRequestRecord) -> LeaveRequestRecord:
        self.session.add(model)
        self.session.flush()
        return model

    def update(self, model: LeaveRequestRecord) -> LeaveRequestRecord:
        self.session.add(model)
        self.session.flush()
        return model

    def update_with_version_check(
        self, model: LeaveRequestRecord, expected_version: int
    ) -> LeaveRequestRecord:
        current = self.get_by_id(model.id)
        if current is None:
            raise ValueError(f"leave request {model.id} not found")
        if current.version != expected_version:
            raise ConflictVersionError(model.id, expected_version, current.version)
        model.version = expected_version + 1
        return self.update(model)

    def _apply_filters(
        self, stmt: Select[tuple[LeaveRequestRecord]], filters: dict[str, object] | None
    ) -> Select[tuple[LeaveRequestRecord]]:
        if not filters:
            return stmt
        if "status" in filters:
            stmt = stmt.where(LeaveRequestRecord.status == filters["status"])
        if "location_id" in filters:
            stmt = stmt.where(LeaveRequestRecord.location_id == filters["location_id"])
        return stmt
