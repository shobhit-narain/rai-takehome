from __future__ import annotations

from src.infra.jobs.scheduler import SchedulerService


def test_scheduler_service_lifecycle() -> None:
    service = SchedulerService()
    service.start()
    service.schedule_job("job-1", lambda: None, trigger="interval", seconds=3600)
    service.cancel_job("job-1")
    service.cancel_job("job-1")
    service.shutdown()
