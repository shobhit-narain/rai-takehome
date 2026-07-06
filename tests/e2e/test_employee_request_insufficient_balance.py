from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header
from tests.helpers.fixtures import build_leave_create_payload


def test_employee_request_insufficient_balance(test_client, employee_user: UserRecord) -> None:
    response = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(leave_duration=999.0),
    )

    assert response.status_code == 409
    body = response.json()
    assert body["code"] == "INSUFFICIENT_BALANCE"
