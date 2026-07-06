from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header
from tests.helpers.fixtures import build_leave_create_payload


def test_ambiguous_hcm_response_moves_request_to_pending_reconciliation(
    test_client, employee_user: UserRecord, mock_hcm_adapter
) -> None:
    mock_hcm_adapter.activate_scenario("ambiguous_success", enabled=True)

    response = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    )

    assert response.status_code == 202
    assert response.json()["code"] == "RECONCILIATION_REQUIRED"
