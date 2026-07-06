from __future__ import annotations

import time

from src.infra.cache.inmemory_cache import InMemoryCacheBackend


def test_cache_key_round_trip() -> None:
    cache = InMemoryCacheBackend()
    cache.set_key("k", "v")
    assert cache.get_key("k") == "v"


def test_cache_namespace_isolation() -> None:
    cache = InMemoryCacheBackend()
    cache.set_key("ns1:k", "v1")
    cache.set_key("ns2:k", "v2")
    assert cache.get_key("ns1:k") == "v1"
    assert cache.get_key("ns2:k") == "v2"


def test_cache_ttl_expiration() -> None:
    cache = InMemoryCacheBackend()
    cache.set_key("k", "v", ttl_seconds=0)
    time.sleep(0.01)
    assert cache.get_key("k") is None


def test_cache_delete_removes_key() -> None:
    cache = InMemoryCacheBackend()
    cache.set_key("k", "v")
    cache.delete_key("k")
    assert cache.get_key("k") is None
