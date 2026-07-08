# Tests for end-to-end ambiguous HCM response handling.
# Validates that ambiguous upstream responses move local state to pending_reconciliation.

from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header
from tests.helpers.fixtures import build_leave_create_payload


# Configure mock HCM to return ambiguous success; verify local status becomes pending_reconciliation
def test_ambiguous_hcm_response_moves_request_to_pending_reconciliation(
    test_client, employee_user: UserRecord, mock_hcm_adapter
) -> None:
    # Enable scenario that returns ambiguous success from HCM
    mock_hcm_adapter.activate_scenario("ambiguous_success", enabled=True)

    response = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    )

    # Should return 202 Accepted with reconciliation required code
    assert response.status_code == 202
    assert response.json()["code"] == "RECONCILIATION_REQUIRED"
