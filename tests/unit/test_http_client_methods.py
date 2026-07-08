# Tests for HttpClient HTTP method coverage (PUT, DELETE).
# Validates that all HTTP methods are correctly passed through to the transport.

from __future__ import annotations

import httpx

from src.infra.http.client import HttpClient
from src.infra.http.retry import RetryPolicy


def _client(handler) -> HttpClient:
    return HttpClient(
        retry_policy=RetryPolicy(max_attempts=1, base_delay=0.0, jitter=0.0),
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


# PUT and DELETE methods correctly pass HTTP method to handler
def test_http_client_put_and_delete() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"method": request.method})

    client = _client(handler)
    assert client.put("https://example.com/r").json()["method"] == "PUT"
    assert client.delete("https://example.com/r").json()["method"] == "DELETE"
