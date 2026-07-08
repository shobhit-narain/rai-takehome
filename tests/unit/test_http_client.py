# Tests for HttpClient infrastructure.
# Validates successful responses, retry logic for transient failures, non-retry on validation errors,
# and typed error handling for timeouts.

from __future__ import annotations

import httpx
import pytest

from src.infra.http.client import HttpClient
from src.infra.http.errors import UpstreamTimeoutError, UpstreamValidationError
from src.infra.http.retry import RetryPolicy


def _client_with_transport(transport: httpx.MockTransport, max_attempts: int = 3) -> HttpClient:
    return HttpClient(
        retry_policy=RetryPolicy(max_attempts=max_attempts, base_delay=0.0, jitter=0.0),
        client=httpx.Client(transport=transport),
    )


# Successful GET request returns parsed JSON response
def test_http_client_returns_successful_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    client = _client_with_transport(httpx.MockTransport(handler))
    response = client.get("https://example.com/resource")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


# Transient 500 error triggers retry and eventually succeeds
def test_http_client_retries_transient_failure() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] < 2:
            return httpx.Response(500)
        return httpx.Response(200, json={"ok": True})

    client = _client_with_transport(httpx.MockTransport(handler))
    response = client.get("https://example.com/resource")
    assert response.status_code == 200
    assert calls["count"] == 2


# 422 validation error is not retried and raises typed error
def test_http_client_does_not_retry_validation_error() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(422)

    client = _client_with_transport(httpx.MockTransport(handler))
    with pytest.raises(UpstreamValidationError):
        client.get("https://example.com/resource")
    assert calls["count"] == 1


# Timeout exception raises typed UpstreamTimeoutError
def test_http_client_timeout_raises_typed_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out", request=request)

    client = _client_with_transport(httpx.MockTransport(handler), max_attempts=1)
    with pytest.raises(UpstreamTimeoutError):
        client.get("https://example.com/resource")
