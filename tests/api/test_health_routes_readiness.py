# Tests for API health/readiness endpoints.
# Validates that the readiness probe endpoint returns success.

from __future__ import annotations


# /ready endpoint returns 200 with ready status
def test_readiness_route_returns_ready(client) -> None:
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
