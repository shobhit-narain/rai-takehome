from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from src.app.config import AppSettings
from src.infra.db.base import Base
from src.infra.db.models import (
    AuditEventRecord,
    HcmConfigRecord,
    LeaveBalanceRecord,
    LeaveRequestRecord,
    ScriptRunRecord,
    UserRecord,
)
from src.infra.db.session import build_engine


class SeedService:
    def __init__(self, session_factory: sessionmaker[Session], data_dir: str | Path | None = None) -> None:
        self.session_factory = session_factory
        self.data_dir = Path(data_dir) if data_dir else Path("seed_data")

    def seed_all(self) -> None:
        self._ensure_schema()
        with self.session_factory() as session:
            self._seed_users(session)
            self._seed_leave_balances(session)
            self._seed_leave_requests(session)
            self._seed_hcm_configs(session)
            self._seed_script_runs(session)
            self._seed_audit_events(session)
            session.commit()

    def _ensure_schema(self) -> None:
        settings = AppSettings()
        engine = build_engine(settings.sqlite_url)
        Base.metadata.create_all(bind=engine)

    def _seed_users(self, session: Session) -> None:
        path = self.data_dir / "users.csv"
        if not path.exists():
            return

        rows = self._read_csv(path)
        existing_ids = {row[0] for row in session.query(UserRecord.id).all()}

        for row in rows:
            if row["id"] in existing_ids:
                continue
            session.add(
                UserRecord(
                    id=row["id"],
                    email=row["email"],
                    name=row["name"],
                    role=row["role"],
                    manager_id=row["manager_id"] or None,
                    location_id=row["location_id"],
                    is_active=self._parse_bool(row["is_active"]),
                    created_ts=self._parse_dt(row["created_ts"]),
                    updated_ts=self._parse_dt(row["updated_ts"]),
                )
            )

    def _seed_leave_balances(self, session: Session) -> None:
        path = self.data_dir / "leave_balances.csv"
        if not path.exists():
            return

        rows = self._read_csv(path)
        existing_ids = {row[0] for row in session.query(LeaveBalanceRecord.id).all()}

        for row in rows:
            if row["id"] in existing_ids:
                continue
            session.add(
                LeaveBalanceRecord(
                    id=row["id"],
                    user_id=row["user_id"],
                    location_id=row["location_id"],
                    leave_type=row["leave_type"],
                    num_available=float(row["num_available"]),
                    num_ytd_taken=float(row["num_ytd_taken"]),
                    num_limit=float(row["num_limit"]),
                    external_updated_ts=self._parse_dt_nullable(row["external_updated_ts"]),
                    updated_ts=self._parse_dt(row["updated_ts"]),
                )
            )

    def _seed_leave_requests(self, session: Session) -> None:
        path = self.data_dir / "leave_requests.csv"
        if not path.exists():
            return

        rows = self._read_csv(path)
        existing_ids = {row[0] for row in session.query(LeaveRequestRecord.id).all()}

        for row in rows:
            if row["id"] in existing_ids:
                continue
            session.add(
                LeaveRequestRecord(
                    id=row["id"],
                    external_hcm_id=row["external_hcm_id"] or None,
                    requestor_id=row["requestor_id"],
                    approver_id=row["approver_id"] or None,
                    location_id=row["location_id"],
                    leave_type=row["leave_type"],
                    leave_duration=float(row["leave_duration"]),
                    leave_start=self._parse_date(row["leave_start"]),
                    leave_end=self._parse_date(row["leave_end"]),
                    status=row["status"],
                    failure_reason=row["failure_reason"] or None,
                    version=int(row["version"]),
                    created_ts=self._parse_dt(row["created_ts"]),
                    updated_ts=self._parse_dt(row["updated_ts"]),
                    approved_ts=self._parse_dt_nullable(row["approved_ts"]),
                    complete_ts=self._parse_dt_nullable(row["complete_ts"]),
                    last_synced_ts=self._parse_dt_nullable(row["last_synced_ts"]),
                )
            )

    def _seed_hcm_configs(self, session: Session) -> None:
        path = self.data_dir / "hcm_configs.csv"
        if not path.exists():
            return

        rows = self._read_csv(path)
        existing_ids = {row[0] for row in session.query(HcmConfigRecord.id).all()}

        for row in rows:
            if row["id"] in existing_ids:
                continue
            session.add(
                HcmConfigRecord(
                    id=row["id"],
                    provider_name=row["provider_name"],
                    base_url=row["base_url"],
                    auth_type=row["auth_type"],
                    token_ref=row["token_ref"],
                    rate_limit_default=int(row["rate_limit_default"]),
                    is_active=self._parse_bool(row["is_active"]),
                    created_ts=self._parse_dt(row["created_ts"]),
                    updated_ts=self._parse_dt(row["updated_ts"]),
                )
            )

    def _seed_script_runs(self, session: Session) -> None:
        path = self.data_dir / "script_runs.csv"
        if not path.exists():
            return

        rows = self._read_csv(path)
        existing_ids = {row[0] for row in session.query(ScriptRunRecord.id).all()}

        for row in rows:
            if row["id"] in existing_ids:
                continue
            session.add(
                ScriptRunRecord(
                    id=row["id"],
                    script_name=row["script_name"],
                    status=row["status"],
                    schedule_expression=row["schedule_expression"] or None,
                    params_json=row["params_json"],
                    started_ts=self._parse_dt_nullable(row["started_ts"]),
                    finished_ts=self._parse_dt_nullable(row["finished_ts"]),
                    cancel_requested=self._parse_bool(row["cancel_requested"]),
                    error_message=row["error_message"] or None,
                )
            )

    def _seed_audit_events(self, session: Session) -> None:
        path = self.data_dir / "audit_events.csv"
        if not path.exists():
            return

        rows = self._read_csv(path)
        existing_ids = {row[0] for row in session.query(AuditEventRecord.id).all()}

        for row in rows:
            if row["id"] in existing_ids:
                continue
            session.add(
                AuditEventRecord(
                    id=row["id"],
                    entity_type=row["entity_type"],
                    entity_id=row["entity_id"],
                    action=row["action"],
                    actor_user_id=row["actor_user_id"],
                    payload_json=row["payload_json"],
                    created_ts=self._parse_dt(row["created_ts"]),
                )
            )

    def _read_csv(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def _parse_dt(self, value: str) -> datetime:
        return datetime.fromisoformat(value)

    def _parse_dt_nullable(self, value: str) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    def _parse_date(self, value: str) -> date:
        return date.fromisoformat(value)

    def _parse_bool(self, value: str) -> bool:
        return value.strip().lower() in {"1", "true", "yes", "y"}