from __future__ import annotations

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from src.app.dependencies import get_db_session
from src.auth.current_user import LoggedInUser
from src.auth.exceptions import ForbiddenRoleError, InvalidTokenError, MissingTokenError
from src.auth.tokens import TokenResolver
from src.repositories.users_repository import UsersRepository


def get_logged_in_user(
    authorization: str | None = Header(default=None),
    db_session: Session = Depends(get_db_session),
) -> LoggedInUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise MissingTokenError("Authorization header with Bearer token is required")

    token = authorization.removeprefix("Bearer ").strip()
    resolver = TokenResolver(UsersRepository(db_session))
    user = resolver.resolve_bearer_token(token)
    if user is None:
        raise InvalidTokenError("token did not resolve to a known user")
    return user


def require_authenticated_user(
    user: LoggedInUser = Depends(get_logged_in_user),
) -> LoggedInUser:
    return user


def require_employee(user: LoggedInUser = Depends(get_logged_in_user)) -> LoggedInUser:
    if not user.is_employee():
        raise ForbiddenRoleError("employee role required")
    return user


def require_manager_or_admin(user: LoggedInUser = Depends(get_logged_in_user)) -> LoggedInUser:
    if not (user.is_manager() or user.is_admin()):
        raise ForbiddenRoleError("manager or admin role required")
    return user


def require_admin(user: LoggedInUser = Depends(get_logged_in_user)) -> LoggedInUser:
    if not user.is_admin():
        raise ForbiddenRoleError("admin role required")
    return user
