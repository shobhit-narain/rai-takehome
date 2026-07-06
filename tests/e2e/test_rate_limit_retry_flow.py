from __future__ import annotations

import httpx

from src.infra.cache.ratelimit import RateLimitService
from src.infra.http.client import HttpClient
from src.infra.http.retry import RetryPolicy


def test_rate_limit_retry_flow() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] < 2:
            return httpx.Response(
                429, headers={"X-RateLimit-Limit": "10", "X-RateLimit-Remaining": "0"}
            )
        return httpx.Response(200, json={"ok": True})

    client = HttpClient(
        retry_policy=RetryPolicy(max_attempts=3, base_delay=0.0, jitter=0.0),
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    rate_limit_service = RateLimitService()

    response = client.get("https://example.com/resource")
    rate_limit_service.update_ratelimit_from_headers(
        "mock_hcm", {"X-RateLimit-Limit": "10", "X-RateLimit-Remaining": "5", "X-RateLimit-Reset": "9999999999"}
    )

    assert response.status_code == 200
    assert calls["count"] == 2
    assert rate_limit_service.get_ratelimit("mock_hcm").remaining == 5
