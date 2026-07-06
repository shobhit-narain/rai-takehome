from __future__ import annotations

from src.infra.cache.redis_stub import RedisCacheBackendStub


def test_redis_stub_round_trip() -> None:
    cache = RedisCacheBackendStub()
    cache.set_key("k", "v")
    assert cache.get_key("k") == "v"
    cache.delete_key("k")
    assert cache.get_key("k") is None
