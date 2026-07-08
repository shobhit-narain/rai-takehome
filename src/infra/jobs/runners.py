from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol


class ScriptRunner(Protocol):
    def run(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any: ...


class LocalScriptRunner:
    def run(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        return fn(*args, **kwargs)


class AirflowRunnerStub:
    def run(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Airflow runner integration is not implemented")
