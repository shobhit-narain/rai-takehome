from __future__ import annotations

from collections.abc import Callable
from typing import Any


class ScriptRegistry:
    def __init__(self) -> None:
        self._scripts: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        self._scripts[name] = fn

    def get(self, name: str) -> Callable[..., Any]:
        if name not in self._scripts:
            raise KeyError(f"script not registered: {name}")
        return self._scripts[name]

    def list_names(self) -> list[str]:
        return list(self._scripts.keys())
