from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from src.infra.db.models import LeaveBalanceRecord, LeaveRequestRecord, UserRecord


def _now() -> datetime:
    return datetime.now(timezone.utc)


def build_user_record(**overrides: object) -> UserRecord:
    defaults: dict[str, object] = dict(
        id=str(uuid.uuid4()),
        email=f"user-{uuid.uuid4().hex[:8]}@example.com",
        name="Test User",
        role="employee",
        manager_id=None,
        location_id="loc-1",
        is_active=True,
        created_ts=_now(),
        updated_ts=_now(),
    )
    defaults.update(overrides)
    return UserRecord(**defaults)


def build_leave_request_record(**overrides: object) -> LeaveRequestRecord:
    defaults: dict[str, object] = dict(
        id=str(uuid.uuid4()),
        external_hcm_id=None,
        requestor_id=str(uuid.uuid4()),
        approver_id=None,
        location_id="loc-1",
        leave_type="vacation",
        leave_duration=1.0,
        leave_start=date.today(),
        leave_end=date.today(),
        status="created",
        failure_reason=None,
        version=1,
        created_ts=_now(),
        updated_ts=_now(),
        approved_ts=None,
        complete_ts=None,
        last_synced_ts=None,
    )
    defaults.update(overrides)
    return LeaveRequestRecord(**defaults)


def build_leave_balance_record(**overrides: object) -> LeaveBalanceRecord:
    defaults: dict[str, object] = dict(
        id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        location_id="loc-1",
        leave_type="vacation",
        num_available=10.0,
        num_ytd_taken=0.0,
        num_limit=10.0,
        external_updated_ts=None,
        updated_ts=_now(),
    )
    defaults.update(overrides)
    return LeaveBalanceRecord(**defaults)
