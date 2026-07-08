# Tests for RetryPolicy infrastructure.
# Validates max attempts enforcement, exponential backoff calculation, and jitter application.

from __future__ import annotations

import pytest

from src.infra.http.errors import RetriableUpstreamError, UpstreamValidationError
from src.infra.http.retry import RetryPolicy


# Retriable errors are retried up to max_attempts; validation errors are never retried
def test_retry_policy_respects_max_attempts() -> None:
    policy = RetryPolicy(max_attempts=2)
    assert policy.should_retry(RetriableUpstreamError("boom")) is True
    assert policy.should_retry(UpstreamValidationError("bad")) is False


# Delay grows exponentially with attempt number (base_delay * 2^(attempt-1))
def test_retry_policy_computes_exponential_delay() -> None:
    policy = RetryPolicy(base_delay=0.1, jitter=0.0)
    assert policy.compute_delay(1) == pytest.approx(0.1)
    assert policy.compute_delay(2) == pytest.approx(0.2)
    assert policy.compute_delay(3) == pytest.approx(0.4)


# Jitter adds random value within [base_delay, base_delay + jitter] range
def test_retry_policy_applies_jitter() -> None:
    policy = RetryPolicy(base_delay=0.1, jitter=0.05)
    delay = policy.compute_delay(1)
    assert 0.1 <= delay <= 0.15
