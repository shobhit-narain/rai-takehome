from __future__ import annotations

import pytest

from src.infra.db.factories import build_leave_request_record, build_user_record
from src.repositories.leave_requests_repository import (
    ConflictVersionError,
    LeaveRequestsRepository,
)


def test_leave_requests_repository_creates_record(db_session) -> None:
    user = build_user_record(id="emp-1")
    db_session.add(user)
    db_session.flush()

    repo = LeaveRequestsRepository(db_session)
    record = build_leave_request_record(id="leave-1", requestor_id="emp-1")
    created = repo.create(record)
    assert repo.get_by_id("leave-1") is created


def test_leave_requests_repository_filters_by_manager_scope(db_session) -> None:
    manager = build_user_record(id="mgr-1", role="manager")
    emp1 = build_user_record(id="emp-1", manager_id="mgr-1")
    emp2 = build_user_record(id="emp-2", manager_id="mgr-1")
    other = build_user_record(id="emp-3")
    db_session.add_all([manager, emp1, emp2, other])
    db_session.flush()

    repo = LeaveRequestsRepository(db_session)
    repo.create(build_leave_request_record(id="leave-1", requestor_id="emp-1"))
    repo.create(build_leave_request_record(id="leave-2", requestor_id="emp-2"))
    repo.create(build_leave_request_record(id="leave-3", requestor_id="emp-3"))

    results = repo.list_for_manager_scope(["emp-1", "emp-2"])
    assert {r.id for r in results} == {"leave-1", "leave-2"}


def test_leave_requests_repository_detects_version_conflict(db_session) -> None:
    user = build_user_record(id="emp-1")
    db_session.add(user)
    db_session.flush()

    repo = LeaveRequestsRepository(db_session)
    record = repo.create(build_leave_request_record(id="leave-1", requestor_id="emp-1", version=1))

    with pytest.raises(ConflictVersionError):
        repo.update_with_version_check(record, expected_version=2)


def test_leave_requests_repository_filters_by_location_id(db_session) -> None:
    user = build_user_record(id="emp-1")
    db_session.add(user)
    db_session.flush()

    repo = LeaveRequestsRepository(db_session)
    repo.create(build_leave_request_record(id="leave-1", requestor_id="emp-1", location_id="loc-1"))
    repo.create(build_leave_request_record(id="leave-2", requestor_id="emp-1", location_id="loc-2"))

    results = repo.list_by_requestor("emp-1", filters={"location_id": "loc-1"})
    assert {r.id for r in results} == {"leave-1"}


def test_leave_requests_repository_update_with_version_check_missing_record(db_session) -> None:
    repo = LeaveRequestsRepository(db_session)
    missing = build_leave_request_record(id="leave-missing", requestor_id="emp-1")

    with pytest.raises(ValueError):
        repo.update_with_version_check(missing, expected_version=1)
