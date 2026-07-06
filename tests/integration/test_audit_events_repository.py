from __future__ import annotations

from datetime import datetime, timezone

from src.infra.db.models import AuditEventRecord
from src.repositories.audit_events_repository import AuditEventsRepository


def _event(**overrides: object) -> AuditEventRecord:
    defaults: dict[str, object] = dict(
        id="evt-1",
        entity_type="leave_request",
        entity_id="leave-1",
        action="created",
        actor_user_id="emp-1",
        payload_json="{}",
        created_ts=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return AuditEventRecord(**defaults)


def test_audit_events_repository_creates_event(db_session) -> None:
    repo = AuditEventsRepository(db_session)
    created = repo.create_event(_event())
    assert repo.list_by_entity("leave_request", "leave-1") == [created]


def test_audit_events_repository_lists_events_by_actor(db_session) -> None:
    repo = AuditEventsRepository(db_session)
    repo.create_event(_event(id="evt-1"))
    repo.create_event(_event(id="evt-2", action="approved"))
    results = repo.list_by_actor("emp-1")
    assert {e.id for e in results} == {"evt-1", "evt-2"}
