from __future__ import annotations

import pytest

from src.infra.http.errors import RetriableUpstreamError, UpstreamValidationError
from src.infra.http.retry import RetryPolicy


def test_retry_policy_respects_max_attempts() -> None:
    policy = RetryPolicy(max_attempts=2)
    assert policy.should_retry(RetriableUpstreamError("boom")) is True
    assert policy.should_retry(UpstreamValidationError("bad")) is False


def test_retry_policy_computes_exponential_delay() -> None:
    policy = RetryPolicy(base_delay=0.1, jitter=0.0)
    assert policy.compute_delay(1) == pytest.approx(0.1)
    assert policy.compute_delay(2) == pytest.approx(0.2)
    assert policy.compute_delay(3) == pytest.approx(0.4)


def test_retry_policy_applies_jitter() -> None:
    policy = RetryPolicy(base_delay=0.1, jitter=0.05)
    delay = policy.compute_delay(1)
    assert 0.1 <= delay <= 0.15
