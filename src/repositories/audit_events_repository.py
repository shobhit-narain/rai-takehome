from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infra.db.models import AuditEventRecord


class AuditEventsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_event(self, event_model: AuditEventRecord) -> AuditEventRecord:
        self.session.add(event_model)
        self.session.flush()
        return event_model

    def list_by_entity(self, entity_type: str, entity_id: str) -> list[AuditEventRecord]:
        stmt = select(AuditEventRecord).where(
            AuditEventRecord.entity_type == entity_type,
            AuditEventRecord.entity_id == entity_id,
        )
        return list(self.session.scalars(stmt).all())

    def list_by_actor(self, actor_user_id: str) -> list[AuditEventRecord]:
        stmt = select(AuditEventRecord).where(AuditEventRecord.actor_user_id == actor_user_id)
        return list(self.session.scalars(stmt).all())
