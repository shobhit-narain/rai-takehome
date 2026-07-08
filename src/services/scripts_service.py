from __future__ import annotations

from typing import Any

from src.infra.db.models import ScriptRunRecord
from src.infra.jobs.registry import ScriptRegistry
from src.infra.jobs.runners import LocalScriptRunner, ScriptRunner
from src.repositories.script_runs_repository import ScriptRunsRepository


class ScriptsService:
    def __init__(
        self,
        script_runs_repository: ScriptRunsRepository,
        registry: ScriptRegistry,
        runner: ScriptRunner | None = None,
    ) -> None:
        self.script_runs_repository = script_runs_repository
        self.registry = registry
        self.runner = runner or LocalScriptRunner()

    def run_script(self, name: str, params: dict[str, Any]) -> ScriptRunRecord:
        fn = self.registry.get(name)
        run = self.script_runs_repository.create_run(name, params)
        self.script_runs_repository.mark_started(run.id)
        try:
            self.runner.run(fn, **params)
        except Exception as exc:  # noqa: BLE001
            return self.script_runs_repository.mark_failed(run.id, str(exc))
        return self.script_runs_repository.mark_completed(run.id)

    def schedule_script(
        self, name: str, cron_expression: str, params: dict[str, Any]
    ) -> ScriptRunRecord:
        self.registry.get(name)
        return self.script_runs_repository.create_run(name, params, schedule_expression=cron_expression)

    def get_status(self, run_id: str) -> ScriptRunRecord | None:
        return self.script_runs_repository.get_by_id(run_id)

    def cancel_run(self, run_id: str) -> ScriptRunRecord:
        return self.script_runs_repository.request_cancel(run_id)
