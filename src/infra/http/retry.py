from __future__ import annotations

import random

from src.infra.http.errors import (
    RetriableUpstreamError,
    UpstreamRateLimitError,
    UpstreamTimeoutError,
)


class RetryPolicy:
    def __init__(self, max_attempts: int = 3, base_delay: float = 0.1, jitter: float = 0.05) -> None:
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.jitter = jitter

    def should_retry(self, exception_or_response: object) -> bool:
        if isinstance(
            exception_or_response,
            (RetriableUpstreamError, UpstreamTimeoutError, UpstreamRateLimitError),
        ):
            return True
        status_code = getattr(exception_or_response, "status_code", None)
        return status_code is not None and status_code >= 500

    def compute_delay(self, attempt_number: int) -> float:
        delay = self.base_delay * (2 ** (attempt_number - 1))
        return delay + random.uniform(0, self.jitter)
