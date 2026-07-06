from __future__ import annotations

import pytest

from src.repositories.script_runs_repository import ScriptRunsRepository


def test_script_runs_repository_marks_run_failed(db_session) -> None:
    repo = ScriptRunsRepository(db_session)
    run = repo.create_run("sync_all_balances", {})

    failed = repo.mark_failed(run.id, "boom")

    assert failed.status == "failed"
    assert failed.error_message == "boom"


def test_script_runs_repository_raises_for_missing_run(db_session) -> None:
    repo = ScriptRunsRepository(db_session)

    with pytest.raises(ValueError):
        repo.mark_started("missing-run")


def test_script_runs_repository_marks_run_completed(db_session) -> None:
    repo = ScriptRunsRepository(db_session)
    run = repo.create_run("sync_all_balances", {})
    repo.mark_started(run.id)
    completed = repo.mark_completed(run.id)
    assert completed.status == "completed"
    assert completed.finished_ts is not None


def test_script_runs_repository_records_cancel_request(db_session) -> None:
    repo = ScriptRunsRepository(db_session)
    run = repo.create_run("reconcile_recent_leaves", {})
    updated = repo.request_cancel(run.id)
    assert updated.cancel_requested is True
