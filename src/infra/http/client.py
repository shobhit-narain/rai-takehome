from __future__ import annotations

import time
from typing import Any

import httpx

from src.infra.http.errors import (
    RetriableUpstreamError,
    UpstreamAuthError,
    UpstreamRateLimitError,
    UpstreamTimeoutError,
    UpstreamValidationError,
)
from src.infra.http.retry import RetryPolicy


class HttpClient:
    def __init__(
        self, retry_policy: RetryPolicy | None = None, client: httpx.Client | None = None
    ) -> None:
        self.retry_policy = retry_policy or RetryPolicy()
        self._client = client or httpx.Client()

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return self._request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return self._request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> httpx.Response:
        return self._request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        return self._request("DELETE", url, **kwargs)

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        attempt = 1
        while True:
            try:
                response = self._client.request(method, url, **kwargs)
            except httpx.TimeoutException as exc:
                error: Exception = UpstreamTimeoutError(str(exc))
                if self.retry_policy.should_retry(error) and attempt < self.retry_policy.max_attempts:
                    time.sleep(self.retry_policy.compute_delay(attempt))
                    attempt += 1
                    continue
                raise error from exc

            mapped_error = self._map_error(response)
            if mapped_error is not None:
                if (
                    self.retry_policy.should_retry(mapped_error)
                    and attempt < self.retry_policy.max_attempts
                ):
                    time.sleep(self.retry_policy.compute_delay(attempt))
                    attempt += 1
                    continue
                raise mapped_error

            return response

    def _map_error(self, response: httpx.Response) -> Exception | None:
        if response.status_code in (401, 403):
            return UpstreamAuthError(f"upstream auth error: {response.status_code}")
        if response.status_code == 429:
            return UpstreamRateLimitError("upstream rate limit exceeded")
        if response.status_code in (400, 422):
            return UpstreamValidationError(f"upstream validation error: {response.status_code}")
        if response.status_code >= 500:
            return RetriableUpstreamError(f"upstream server error: {response.status_code}")
        return None
