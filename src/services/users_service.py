from __future__ import annotations

from src.infra.db.models import UserRecord
from src.repositories.users_repository import UsersRepository


class UsersService:
    def __init__(self, users_repository: UsersRepository) -> None:
        self.users_repository = users_repository

    def get_user(self, user_id: str) -> UserRecord | None:
        return self.users_repository.get_by_id(user_id)

    def get_reporting_tree(self, manager_user_id: str) -> list[UserRecord]:
        return self.users_repository.list_reporting_tree(manager_user_id)

    def is_manager_of(self, manager_user_id: str, employee_user_id: str) -> bool:
        tree_ids = {user.id for user in self.get_reporting_tree(manager_user_id)}
        return employee_user_id in tree_ids
