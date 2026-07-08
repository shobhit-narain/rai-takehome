# Tests for SeedService database seeding functionality.
# Validates CSV-based user loading and idempotent seeding behavior.

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.infra.db.models import UserRecord
from src.infra.db.seed import SeedService
from src.infra.db.session import build_engine, get_session_factory


# seed_all loads users from CSV and is idempotent (re-running doesn't duplicate records)
def test_seed_all_loads_users_from_csv_and_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "seed_test.db"
    monkeypatch.setenv("SQLITE_URL", f"sqlite:///{db_path}")

    data_dir = tmp_path / "seed_data"
    data_dir.mkdir()
    with (data_dir / "users.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "email",
                "name",
                "role",
                "manager_id",
                "location_id",
                "is_active",
                "created_ts",
                "updated_ts",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "id": "user_emp_00001",
                "email": "emp1@example.com",
                "name": "Employee One",
                "role": "employee",
                "manager_id": "",
                "location_id": "loc_us_ca",
                "is_active": "true",
                "created_ts": "2026-01-01T00:00:00",
                "updated_ts": "2026-01-01T00:00:00",
            }
        )

    engine = build_engine(f"sqlite:///{db_path}")
    session_factory = get_session_factory(engine)
    seed_service = SeedService(session_factory, data_dir=data_dir)

    # First seed: should create the user
    seed_service.seed_all()

    with session_factory() as session:
        user = session.get(UserRecord, "user_emp_00001")
        assert user is not None
        assert user.email == "emp1@example.com"

    # Second seed: should not duplicate (idempotent)
    seed_service.seed_all()
    with session_factory() as session:
        assert session.query(UserRecord).count() == 1
