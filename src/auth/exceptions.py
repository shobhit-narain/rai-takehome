from __future__ import annotations


class AuthError(Exception):
    status_code: int = 401


class MissingTokenError(AuthError):
    status_code = 401


class InvalidTokenError(AuthError):
    status_code = 401


class ForbiddenRoleError(AuthError):
    status_code = 403
