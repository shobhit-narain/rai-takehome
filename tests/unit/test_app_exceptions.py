# Tests for application exception classes.
# Validates default error codes and message handling for all custom exception types.

from __future__ import annotations

from src.app.exceptions import (
    AccessDeniedError,
    AppError,
    AuthRequiredError,
    ConflictError,
    ResourceNotFoundError,
    UpstreamDependencyError,
    ValidationFailedError,
)


# Base AppError uses default code and preserves message
def test_app_error_default_code() -> None:
    error = AppError("boom")
    assert error.code == "app_error"
    assert error.message == "boom"


# Specific exception subclasses have correct error codes
def test_specific_error_codes() -> None:
    assert AuthRequiredError().code == "auth_required"
    assert AccessDeniedError().code == "access_denied"
    assert ValidationFailedError().code == "validation_failed"
    assert ConflictError().code == "conflict"
    assert ResourceNotFoundError().code == "not_found"
    assert UpstreamDependencyError().code == "upstream_dependency_error"
