from __future__ import annotations

from src.auth.current_user import LoggedInUser
from src.domain.enums import UserRole


def _user(role: UserRole) -> LoggedInUser:
    return LoggedInUser(user_id="u1", role=role, manager_id=None, location_id="loc-1")


def test_is_employee_returns_true_only_for_employee() -> None:
    assert _user(UserRole.EMPLOYEE).is_employee() is True
    assert _user(UserRole.MANAGER).is_employee() is False
    assert _user(UserRole.ADMIN).is_employee() is False


def test_is_manager_returns_true_only_for_manager() -> None:
    assert _user(UserRole.MANAGER).is_manager() is True
    assert _user(UserRole.EMPLOYEE).is_manager() is False
    assert _user(UserRole.ADMIN).is_manager() is False


def test_is_admin_returns_true_only_for_admin() -> None:
    assert _user(UserRole.ADMIN).is_admin() is True
    assert _user(UserRole.EMPLOYEE).is_admin() is False
    assert _user(UserRole.MANAGER).is_admin() is False
