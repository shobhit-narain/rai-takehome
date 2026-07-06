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


def test_app_error_default_code() -> None:
    error = AppError("boom")
    assert error.code == "app_error"
    assert error.message == "boom"


def test_specific_error_codes() -> None:
    assert AuthRequiredError().code == "auth_required"
    assert AccessDeniedError().code == "access_denied"
    assert ValidationFailedError().code == "validation_failed"
    assert ConflictError().code == "conflict"
    assert ResourceNotFoundError().code == "not_found"
    assert UpstreamDependencyError().code == "upstream_dependency_error"
