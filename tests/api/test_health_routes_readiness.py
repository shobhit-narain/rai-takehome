from __future__ import annotations


def test_readiness_route_returns_ready(client) -> None:
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
