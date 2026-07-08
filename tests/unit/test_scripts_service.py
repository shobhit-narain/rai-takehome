# Tests for ScriptsService domain logic.
# Validates script execution, error handling, scheduling, status lookup, and cancellation.

from __future__ import annotations

import pytest

from src.infra.jobs.registry import ScriptRegistry
from src.infra.jobs.runners import LocalScriptRunner
from src.repositories.script_runs_repository import ScriptRunsRepository
from src.services.scripts_service import ScriptsService


# Running a registered script creates a completed script run record
def test_run_script_creates_script_run_record(db_session) -> None:
    registry = ScriptRegistry()
    registry.register("noop", lambda: None)
    service = ScriptsService(ScriptRunsRepository(db_session), registry, LocalScriptRunner())

    run = service.run_script("noop", {})

    assert run.status == "completed"


# Running an unknown script name raises KeyError
def test_unknown_script_name_raises_error(db_session) -> None:
    registry = ScriptRegistry()
    service = ScriptsService(ScriptRunsRepository(db_session), registry, LocalScriptRunner())

    with pytest.raises(KeyError):
        service.run_script("unknown", {})


# Script that raises exception is marked as failed with error message
def test_run_script_marks_failed_on_exception(db_session) -> None:
    registry = ScriptRegistry()

    def _boom() -> None:
        raise RuntimeError("boom")

    registry.register("boom", _boom)
    service = ScriptsService(ScriptRunsRepository(db_session), registry, LocalScriptRunner())

    run = service.run_script("boom", {})

    assert run.status == "failed"
    assert run.error_message == "boom"


# Scheduling a script persists the cron expression
def test_schedule_script_persists_schedule_expression(db_session) -> None:
    registry = ScriptRegistry()
    registry.register("noop", lambda: None)
    service = ScriptsService(ScriptRunsRepository(db_session), registry, LocalScriptRunner())

    run = service.schedule_script("noop", "0 * * * *", {})

    assert run.schedule_expression == "0 * * * *"


# get_status retrieves the correct script run by ID
def test_get_status_returns_run(db_session) -> None:
    registry = ScriptRegistry()
    registry.register("noop", lambda: None)
    service = ScriptsService(ScriptRunsRepository(db_session), registry, LocalScriptRunner())

    run = service.run_script("noop", {})

    assert service.get_status(run.id).id == run.id


# cancel_run marks the run with cancellation requested flag
def test_cancel_run_marks_cancellation_requested(db_session) -> None:
    registry = ScriptRegistry()
    registry.register("noop", lambda: None)
    service = ScriptsService(ScriptRunsRepository(db_session), registry, LocalScriptRunner())

    run = service.run_script("noop", {})
    canceled = service.cancel_run(run.id)

    assert canceled.cancel_requested is True
