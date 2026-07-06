from __future__ import annotations

from dataclasses import dataclass

from src.domain.enums import UserRole


@dataclass
class LoggedInUser:
    user_id: str
    role: UserRole
    manager_id: str | None
    location_id: str

    def is_employee(self) -> bool:
        return self.role == UserRole.EMPLOYEE

    def is_manager(self) -> bool:
        return self.role == UserRole.MANAGER

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
