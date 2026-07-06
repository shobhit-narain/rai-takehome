from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class CacheBackend(Protocol):
    def get_key(self, key: str) -> str | None: ...

    def set_key(self, key: str, value: str, ttl_seconds: int | None = None) -> None: ...

    def delete_key(self, key: str) -> None: ...


@dataclass
class RateLimitState:
    provider: str
    limit: int
    remaining: int
    reset_at: float
