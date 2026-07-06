from __future__ import annotations

from src.infra.db.factories import build_user_record
from src.repositories.users_repository import UsersRepository
from src.services.users_service import UsersService


def test_get_user_returns_record(db_session) -> None:
    db_session.add(build_user_record(id="emp-1"))
    db_session.flush()
    service = UsersService(UsersRepository(db_session))

    assert service.get_user("emp-1").id == "emp-1"


def test_is_manager_of_checks_reporting_tree(db_session) -> None:
    db_session.add(build_user_record(id="mgr-1", role="manager"))
    db_session.add(build_user_record(id="emp-1", manager_id="mgr-1"))
    db_session.add(build_user_record(id="emp-2"))
    db_session.flush()
    service = UsersService(UsersRepository(db_session))

    assert service.is_manager_of("mgr-1", "emp-1") is True
    assert service.is_manager_of("mgr-1", "emp-2") is False
