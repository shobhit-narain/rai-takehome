from __future__ import annotations

from src.infra.cache.inmemory_cache import InMemoryCacheBackend


class RedisCacheBackendStub(InMemoryCacheBackend):
    """In-process stand-in for a Redis-backed cache, sharing the same interface."""
