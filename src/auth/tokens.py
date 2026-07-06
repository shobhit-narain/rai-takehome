from __future__ import annotations

from src.auth.current_user import LoggedInUser
from src.domain.enums import UserRole
from src.repositories.users_repository import UsersRepository


class TokenResolver:
    def __init__(self, users_repository: UsersRepository) -> None:
        self.users_repository = users_repository

    def resolve_bearer_token(self, token: str) -> LoggedInUser | None:
        user = self.users_repository.get_by_id(token)
        if user is None or not user.is_active:
            return None
        return LoggedInUser(
            user_id=user.id,
            role=UserRole(user.role),
            manager_id=user.manager_id,
            location_id=user.location_id,
        )
