from __future__ import annotations


class AppError(Exception):
    def __init__(self, message: str, *, code: str = "app_error") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class AuthRequiredError(AppError):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message, code="auth_required")


class AccessDeniedError(AppError):
    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(message, code="access_denied")


class ValidationFailedError(AppError):
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, code="validation_failed")


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(message, code="conflict")


class ResourceNotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, code="not_found")


class UpstreamDependencyError(AppError):
    def __init__(self, message: str = "Upstream dependency error") -> None:
        super().__init__(message, code="upstream_dependency_error")
