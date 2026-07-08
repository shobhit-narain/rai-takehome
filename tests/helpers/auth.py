from __future__ import annotations

from src.auth.current_user import LoggedInUser
from src.domain.enums import UserRole


def make_auth_header(user_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {user_id}"}


def make_employee_user(
    user_id: str = "user_emp_00001", manager_id: str | None = "user_mgr_0001"
) -> LoggedInUser:
    return LoggedInUser(
        user_id=user_id, role=UserRole.EMPLOYEE, manager_id=manager_id, location_id="loc_us_ca"
    )


def make_manager_user(user_id: str = "user_mgr_0001") -> LoggedInUser:
    return LoggedInUser(user_id=user_id, role=UserRole.MANAGER, manager_id=None, location_id="loc_us_ca")


def make_admin_user(user_id: str = "user_admin_0001") -> LoggedInUser:
    return LoggedInUser(user_id=user_id, role=UserRole.ADMIN, manager_id=None, location_id="loc_us_ca")
