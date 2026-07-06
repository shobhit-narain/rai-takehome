from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from src.adapters.hcm.mock_hcm_adapter import MockHcmAdapter
from src.auth.current_user import LoggedInUser
from src.domain.enums import LeaveAction, LeaveType, UserRole
from src.domain.leave_policy import LeavePolicyService
from src.domain.leave_state_machine import LeaveStateMachine
from src.domain.models import LeaveCreateCommand, LeaveUpdateCommand
from src.infra.db.factories import build_user_record
from src.repositories.audit_events_repository import AuditEventsRepository
from src.repositories.leave_requests_repository import (
    ConflictVersionError,
    LeaveRequestsRepository,
)
from src.repositories.users_repository import UsersRepository
from src.services.audit_service import AuditService
from src.services.leaves_service import LeavesService
from src.services.users_service import UsersService
from tests.helpers.mock_hcm import build_mock_hcm_state, write_mock_hcm_state


def _build_service(db_session, tmp_path: Path) -> LeavesService:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json", build_mock_hcm_state())
    hcm_adapter = MockHcmAdapter(state_file=state_file)
    return LeavesService(
        leave_requests_repository=LeaveRequestsRepository(db_session),
        hcm_service=hcm_adapter,
        policy_service=LeavePolicyService(),
        state_machine=LeaveStateMachine(),
        audit_service=AuditService(AuditEventsRepository(db_session)),
        users_service=UsersService(UsersRepository(db_session)),
    )


def test_leaves_service_persists_request_and_audit_event(db_session, tmp_path: Path) -> None:
    db_session.add(build_user_record(id="user_emp_00001", role="employee"))
    db_session.flush()

    service = _build_service(db_session, tmp_path)
    actor = LoggedInUser(
        user_id="user_emp_00001", role=UserRole.EMPLOYEE, manager_id="user_mgr_0001", location_id="loc_us_ca"
    )
    command = LeaveCreateCommand(
        leave_type=LeaveType.PTO,
        leave_duration=1.0,
        leave_start=date(2026, 9, 10),
        leave_end=date(2026, 9, 10),
        location_id="loc_us_ca",
    )

    record = service.request_leave(actor, command)

    assert record.status == "requested"
    events = AuditEventsRepository(db_session).list_by_entity("leave_request", record.id)
    assert len(events) == 1


def test_leaves_service_approves_valid_request(db_session, tmp_path: Path) -> None:
    db_session.add(build_user_record(id="user_mgr_0001", role="manager"))
    db_session.add(
        build_user_record(id="user_emp_00001", role="employee", manager_id="user_mgr_0001")
    )
    db_session.flush()

    service = _build_service(db_session, tmp_path)
    employee = LoggedInUser(
        user_id="user_emp_00001", role=UserRole.EMPLOYEE, manager_id="user_mgr_0001", location_id="loc_us_ca"
    )
    manager = LoggedInUser(user_id="user_mgr_0001", role=UserRole.MANAGER, manager_id=None, location_id="loc_us_ca")

    command = LeaveCreateCommand(
        leave_type=LeaveType.PTO,
        leave_duration=1.0,
        leave_start=date(2026, 9, 10),
        leave_end=date(2026, 9, 10),
        location_id="loc_us_ca",
    )
    record = service.request_leave(employee, command)

    updated = service.update_leave_request(
        manager, record.id, LeaveUpdateCommand(action=LeaveAction.APPROVE)
    )

    assert updated.status == "approved"


def test_leaves_service_detects_version_conflict(db_session, tmp_path: Path) -> None:
    db_session.add(build_user_record(id="user_emp_00001", role="employee"))
    db_session.flush()

    service = _build_service(db_session, tmp_path)
    actor = LoggedInUser(
        user_id="user_emp_00001", role=UserRole.EMPLOYEE, manager_id="user_mgr_0001", location_id="loc_us_ca"
    )
    command = LeaveCreateCommand(
        leave_type=LeaveType.PTO,
        leave_duration=1.0,
        leave_start=date(2026, 9, 10),
        leave_end=date(2026, 9, 10),
        location_id="loc_us_ca",
    )
    record = service.request_leave(actor, command)

    with pytest.raises(ConflictVersionError):
        service.leave_requests_repository.update_with_version_check(record, expected_version=999)
