from __future__ import annotations

import time

from src.infra.cache.interfaces import RateLimitState


class RateLimitService:
    def __init__(self) -> None:
        self._state: dict[str, RateLimitState] = {}

    def get_ratelimit(self, provider: str) -> RateLimitState | None:
        return self._state.get(provider)

    def acquire_ratelimit(self, provider: str, tokens: int = 1) -> bool:
        state = self._state.get(provider)
        if state is None:
            return True
        if state.reset_at < time.time():
            del self._state[provider]
            return True
        if state.remaining < tokens:
            return False
        state.remaining -= tokens
        return True

    def update_ratelimit_from_headers(
        self, provider: str, headers: dict[str, str]
    ) -> RateLimitState:
        limit = int(headers.get("X-RateLimit-Limit", 0))
        remaining = int(headers.get("X-RateLimit-Remaining", 0))
        reset_at = float(headers.get("X-RateLimit-Reset", time.time()))
        state = RateLimitState(provider=provider, limit=limit, remaining=remaining, reset_at=reset_at)
        self._state[provider] = state
        return state
