from __future__ import annotations

import time


class InMemoryCacheBackend:
    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float | None]] = {}

    def get_key(self, key: str) -> str | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at is not None and expires_at < time.monotonic():
            del self._store[key]
            return None
        return value

    def set_key(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        expires_at = time.monotonic() + ttl_seconds if ttl_seconds is not None else None
        self._store[key] = (value, expires_at)

    def delete_key(self, key: str) -> None:
        self._store.pop(key, None)
