# Tests for authentication dependency functions.
# Validates bearer token validation and role-based access control (employee, manager, admin).

from __future__ import annotations

import pytest

from src.auth.dependencies import (
    get_logged_in_user,
    require_admin,
    require_employee,
    require_manager_or_admin,
)
from src.auth.exceptions import ForbiddenRoleError, InvalidTokenError, MissingTokenError
from src.infra.db.factories import build_user_record


# Missing Authorization header raises MissingTokenError
def test_missing_bearer_token_returns_401(db_session) -> None:
    with pytest.raises(MissingTokenError):
        get_logged_in_user(authorization=None, db_session=db_session)


# Invalid/unknown bearer token raises InvalidTokenError
def test_invalid_token_returns_401(db_session) -> None:
    with pytest.raises(InvalidTokenError):
        get_logged_in_user(authorization="Bearer unknown-user", db_session=db_session)


# Valid employee token is accepted by employee dependency
def test_employee_dependency_accepts_employee(db_session) -> None:
    db_session.add(build_user_record(id="emp-1", role="employee"))
    db_session.flush()
    user = get_logged_in_user(authorization="Bearer emp-1", db_session=db_session)

    assert require_employee(user) is user


# Employee role is rejected by manager-or-admin dependency
def test_manager_dependency_rejects_employee(db_session) -> None:
    db_session.add(build_user_record(id="emp-1", role="employee"))
    db_session.flush()
    user = get_logged_in_user(authorization="Bearer emp-1", db_session=db_session)

    with pytest.raises(ForbiddenRoleError):
        require_manager_or_admin(user)


# Manager role is rejected by admin-only dependency
def test_admin_dependency_rejects_manager(db_session) -> None:
    db_session.add(build_user_record(id="mgr-1", role="manager"))
    db_session.flush()
    user = get_logged_in_user(authorization="Bearer mgr-1", db_session=db_session)

    with pytest.raises(ForbiddenRoleError):
        require_admin(user)
