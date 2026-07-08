# Tests for UsersRepository integration with database.
# Validates reporting tree traversal (including indirect reports) and direct reports retrieval.

from __future__ import annotations

from src.infra.db.factories import build_user_record
from src.repositories.users_repository import UsersRepository


# list_reporting_tree returns both direct and indirect reports recursively
def test_users_repository_returns_reporting_tree(db_session) -> None:
    manager = build_user_record(id="mgr-1", role="manager")
    report1 = build_user_record(id="emp-1", role="employee", manager_id="mgr-1")
    report2 = build_user_record(id="emp-2", role="employee", manager_id="emp-1")
    db_session.add_all([manager, report1, report2])
    db_session.flush()

    repo = UsersRepository(db_session)
    tree = repo.list_reporting_tree("mgr-1")
    assert {user.id for user in tree} == {"emp-1", "emp-2"}


# list_reports returns only direct reports (not indirect)
def test_users_repository_returns_direct_reports(db_session) -> None:
    manager = build_user_record(id="mgr-1", role="manager")
    report1 = build_user_record(id="emp-1", role="employee", manager_id="mgr-1")
    report2 = build_user_record(id="emp-2", role="employee", manager_id="mgr-1")
    db_session.add_all([manager, report1, report2])
    db_session.flush()

    repo = UsersRepository(db_session)
    reports = repo.list_reports("mgr-1")
    assert {user.id for user in reports} == {"emp-1", "emp-2"}
