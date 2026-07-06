from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infra.db.models import UserRecord


class UsersRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: str) -> UserRecord | None:
        return self.session.get(UserRecord, user_id)

    def list_all(self) -> list[UserRecord]:
        return list(self.session.scalars(select(UserRecord)).all())

    def list_reports(self, manager_user_id: str) -> list[UserRecord]:
        stmt = select(UserRecord).where(UserRecord.manager_id == manager_user_id)
        return list(self.session.scalars(stmt).all())

    def list_reporting_tree(self, manager_user_id: str) -> list[UserRecord]:
        result: list[UserRecord] = []
        seen: set[str] = {manager_user_id}
        frontier = [manager_user_id]
        while frontier:
            next_frontier: list[str] = []
            for manager_id in frontier:
                for report in self.list_reports(manager_id):
                    if report.id not in seen:
                        seen.add(report.id)
                        result.append(report)
                        next_frontier.append(report.id)
            frontier = next_frontier
        return result
