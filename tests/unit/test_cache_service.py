# Tests for InMemoryCacheBackend infrastructure.
# Validates basic cache operations: get/set, namespace isolation, TTL expiration, and key deletion.

from __future__ import annotations

import time

from src.infra.cache.inmemory_cache import InMemoryCacheBackend


# Basic set and get operations work correctly
def test_cache_key_round_trip() -> None:
    cache = InMemoryCacheBackend()
    cache.set_key("k", "v")
    assert cache.get_key("k") == "v"


# Namespace isolation prevents key collisions across namespaces
def test_cache_namespace_isolation() -> None:
    cache = InMemoryCacheBackend()
    cache.set_key("ns1:k", "v1")
    cache.set_key("ns2:k", "v2")
    assert cache.get_key("ns1:k") == "v1"
    assert cache.get_key("ns2:k") == "v2"


# TTL expiration removes key after specified time
def test_cache_ttl_expiration() -> None:
    cache = InMemoryCacheBackend()
    cache.set_key("k", "v", ttl_seconds=0)
    time.sleep(0.01)
    assert cache.get_key("k") is None


# Delete operation removes key from cache
def test_cache_delete_removes_key() -> None:
    cache = InMemoryCacheBackend()
    cache.set_key("k", "v")
    cache.delete_key("k")
    assert cache.get_key("k") is None
