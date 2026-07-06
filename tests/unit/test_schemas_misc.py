from __future__ import annotations

from src.api.schemas.auth import AuthenticatedUserResponse
from src.api.schemas.common import ErrorResponse, PaginationMeta


def test_authenticated_user_response_round_trip() -> None:
    response = AuthenticatedUserResponse(
        user_id="u1", role="employee", manager_id="mgr-1", location_id="loc-1"
    )
    assert response.user_id == "u1"


def test_error_response_defaults() -> None:
    error = ErrorResponse(code="VALIDATION_ERROR", message="bad input")
    assert error.details == {}
    assert error.request_id is None


def test_pagination_meta_fields() -> None:
    meta = PaginationMeta(page=1, page_size=50, total_items=100, total_pages=2)
    assert meta.total_pages == 2
