from __future__ import annotations

from typing import Any, Callable

from apscheduler.schedulers.background import BackgroundScheduler


class SchedulerService:
    def __init__(self) -> None:
        self._scheduler = BackgroundScheduler()

    def start(self) -> None:
        if not self._scheduler.running:
            self._scheduler.start()

    def shutdown(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    def schedule_job(
        self, job_id: str, fn: Callable[..., Any], trigger: str = "interval", **trigger_args: Any
    ) -> None:
        self._scheduler.add_job(fn, trigger=trigger, id=job_id, replace_existing=True, **trigger_args)

    def cancel_job(self, job_id: str) -> None:
        if self._scheduler.get_job(job_id) is not None:
            self._scheduler.remove_job(job_id)
