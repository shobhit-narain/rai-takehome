# Tests for health check API routes.
# Validates /api/v1/health endpoint returns successful response.

from __future__ import annotations


# Health endpoint returns 200 OK with expected JSON body
def test_health_route_returns_ok(client) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
