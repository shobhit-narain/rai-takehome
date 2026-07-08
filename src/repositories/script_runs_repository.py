from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.infra.db.models import ScriptRunRecord


class ScriptRunsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_run(
        self, script_name: str, params: dict[str, object], schedule_expression: str | None = None
    ) -> ScriptRunRecord:
        record = ScriptRunRecord(
            id=str(uuid.uuid4()),
            script_name=script_name,
            status="pending",
            schedule_expression=schedule_expression,
            params_json=json.dumps(params),
            cancel_requested=False,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def get_by_id(self, run_id: str) -> ScriptRunRecord | None:
        return self.session.get(ScriptRunRecord, run_id)

    def mark_started(self, run_id: str) -> ScriptRunRecord:
        record = self._require(run_id)
        record.status = "running"
        record.started_ts = datetime.now(UTC)
        self.session.flush()
        return record

    def mark_completed(self, run_id: str) -> ScriptRunRecord:
        record = self._require(run_id)
        record.status = "completed"
        record.finished_ts = datetime.now(UTC)
        self.session.flush()
        return record

    def mark_failed(self, run_id: str, error_message: str) -> ScriptRunRecord:
        record = self._require(run_id)
        record.status = "failed"
        record.finished_ts = datetime.now(UTC)
        record.error_message = error_message
        self.session.flush()
        return record

    def request_cancel(self, run_id: str) -> ScriptRunRecord:
        record = self._require(run_id)
        record.cancel_requested = True
        self.session.flush()
        return record

    def _require(self, run_id: str) -> ScriptRunRecord:
        record = self.get_by_id(run_id)
        if record is None:
            raise ValueError(f"script run {run_id} not found")
        return record
