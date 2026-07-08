from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from src.auth.current_user import LoggedInUser
from src.infra.db.models import AuditEventRecord, LeaveRequestRecord
from src.repositories.audit_events_repository import AuditEventsRepository


class AuditService:
    def __init__(self, audit_events_repository: AuditEventsRepository) -> None:
        self.audit_events_repository = audit_events_repository

    def record_leave_created(
        self, actor: LoggedInUser, leave_request: LeaveRequestRecord
    ) -> AuditEventRecord:
        return self._record(
            "leave_request", leave_request.id, "created", actor.user_id, {"status": leave_request.status}
        )

    def record_leave_updated(
        self, actor: LoggedInUser, leave_request: LeaveRequestRecord, action: str
    ) -> AuditEventRecord:
        return self._record(
            "leave_request", leave_request.id, action, actor.user_id, {"status": leave_request.status}
        )

    def record_reconciliation(
        self, actor_label: str, entity_id: str, result: dict[str, Any]
    ) -> AuditEventRecord:
        return self._record("reconciliation", entity_id, "reconciled", actor_label, result)

    def _record(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        actor_user_id: str,
        payload: dict[str, Any],
    ) -> AuditEventRecord:
        event = AuditEventRecord(
            id=str(uuid.uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_user_id=actor_user_id,
            payload_json=json.dumps(payload),
            created_ts=datetime.now(UTC),
        )
        return self.audit_events_repository.create_event(event)
