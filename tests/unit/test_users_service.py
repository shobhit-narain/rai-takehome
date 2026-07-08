# Tests for UsersService domain logic.
# Validates user retrieval and manager-of relationship checking via reporting tree.

from __future__ import annotations

from src.infra.db.factories import build_user_record
from src.repositories.users_repository import UsersRepository
from src.services.users_service import UsersService


# get_user returns the correct user record by ID
def test_get_user_returns_record(db_session) -> None:
    db_session.add(build_user_record(id="emp-1"))
    db_session.flush()
    service = UsersService(UsersRepository(db_session))

    assert service.get_user("emp-1").id == "emp-1"


# is_manager_of returns True for direct/indirect reports, False for unrelated employees
def test_is_manager_of_checks_reporting_tree(db_session) -> None:
    db_session.add(build_user_record(id="mgr-1", role="manager"))
    db_session.add(build_user_record(id="emp-1", manager_id="mgr-1"))
    db_session.add(build_user_record(id="emp-2"))
    db_session.flush()
    service = UsersService(UsersRepository(db_session))

    assert service.is_manager_of("mgr-1", "emp-1") is True
    assert service.is_manager_of("mgr-1", "emp-2") is False
