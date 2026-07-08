# Tests for LeaveBalancesRepository integration with database.
# Validates bulk upsert behavior and unique constraint enforcement on user-location-leave_type.

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError

from src.infra.db.factories import build_leave_balance_record, build_user_record
from src.infra.db.models import LeaveBalanceRecord
from src.repositories.leave_balances_repository import LeaveBalancesRepository


# bulk_upsert updates existing balance row when unique key matches
def test_leave_balances_repository_bulk_upsert_updates_existing_rows(db_session) -> None:
    user = build_user_record(id="emp-1")
    db_session.add(user)
    db_session.flush()

    repo = LeaveBalancesRepository(db_session)
    repo.upsert(
        build_leave_balance_record(id="bal-1", user_id="emp-1", leave_type="vacation", num_available=10.0)
    )

    repo.bulk_upsert(
        [build_leave_balance_record(id="bal-2", user_id="emp-1", leave_type="vacation", num_available=7.0)]
    )

    rows = repo.list_for_user("emp-1")
    assert len(rows) == 1
    assert rows[0].num_available == 7.0


# Unique constraint on (user_id, location_id, leave_type) prevents duplicate rows
def test_leave_balances_repository_enforces_unique_scope(db_session) -> None:
    user = build_user_record(id="emp-1")
    db_session.add(user)
    db_session.flush()

    now = datetime.now(UTC)
    db_session.add(
        LeaveBalanceRecord(
            id="bal-1",
            user_id="emp-1",
            location_id="loc-1",
            leave_type="vacation",
            num_available=1.0,
            num_ytd_taken=0.0,
            num_limit=1.0,
            external_updated_ts=None,
            updated_ts=now,
        )
    )
    db_session.flush()

    db_session.add(
        LeaveBalanceRecord(
            id="bal-2",
            user_id="emp-1",
            location_id="loc-1",
            leave_type="vacation",
            num_available=2.0,
            num_ytd_taken=0.0,
            num_limit=2.0,
            external_updated_ts=None,
            updated_ts=now,
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
