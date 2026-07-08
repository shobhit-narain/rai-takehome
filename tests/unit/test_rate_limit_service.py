# Tests for RateLimitService infrastructure.
# Validates rate-limit header parsing, cached state updates, and token acquisition logic.

from __future__ import annotations

import time

from src.infra.cache.ratelimit import RateLimitService


# Rate-limit headers are parsed and cached state is updated correctly
def test_rate_limit_headers_update_cached_state() -> None:
    service = RateLimitService()
    state = service.update_ratelimit_from_headers(
        "mock_hcm",
        {
            "X-RateLimit-Limit": "10",
            "X-RateLimit-Remaining": "5",
            "X-RateLimit-Reset": str(time.time() + 60),
        },
    )
    assert state.limit == 10
    assert service.get_ratelimit("mock_hcm") is state


# Acquire succeeds when rate-limit tokens are available
def test_acquire_ratelimit_succeeds_when_tokens_available() -> None:
    service = RateLimitService()
    service.update_ratelimit_from_headers(
        "mock_hcm",
        {
            "X-RateLimit-Limit": "10",
            "X-RateLimit-Remaining": "5",
            "X-RateLimit-Reset": str(time.time() + 60),
        },
    )
    assert service.acquire_ratelimit("mock_hcm", tokens=1) is True


# Acquire fails when rate-limit tokens are exhausted
def test_acquire_ratelimit_fails_when_tokens_unavailable() -> None:
    service = RateLimitService()
    service.update_ratelimit_from_headers(
        "mock_hcm",
        {
            "X-RateLimit-Limit": "10",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(time.time() + 60),
        },
    )
    assert service.acquire_ratelimit("mock_hcm", tokens=1) is False
