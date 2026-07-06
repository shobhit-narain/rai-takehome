from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.adapters.hcm.mock_hcm_adapter import MockHcmAdapter
from src.adapters.hcm.port import HcmServicePort
from src.app.config import AppSettings
from src.domain.leave_policy import LeavePolicyService
from src.domain.leave_state_machine import LeaveStateMachine
from src.infra.cache.inmemory_cache import InMemoryCacheBackend
from src.infra.cache.interfaces import CacheBackend
from src.infra.cache.ratelimit import RateLimitService
from src.infra.db.base import Base
from src.infra.db.session import build_engine, get_session_factory
from src.infra.http.client import HttpClient
from src.infra.jobs.registry import ScriptRegistry
from src.infra.jobs.runners import LocalScriptRunner
from src.infra.jobs.scripts import (
    backfill_balances_script,
    reconcile_recent_leaves_script,
    repair_pending_reconciliation_script,
    sync_all_balances_script,
)
from src.repositories.audit_events_repository import AuditEventsRepository
from src.repositories.leave_balances_repository import LeaveBalancesRepository
from src.repositories.leave_requests_repository import LeaveRequestsRepository
from src.repositories.script_runs_repository import ScriptRunsRepository
from src.repositories.users_repository import UsersRepository
from src.services.audit_service import AuditService
from src.services.balances_service import BalancesService
from src.services.leaves_service import LeavesService
from src.services.reconciliation_service import ReconciliationService
from src.services.scripts_service import ScriptsService
from src.services.users_service import UsersService

_cache_backend = InMemoryCacheBackend()
_rate_limit_service = RateLimitService()
_http_client = HttpClient()
_hcm_service = MockHcmAdapter()
_script_registry = ScriptRegistry()


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()


@lru_cache
def _get_engine() -> Engine:
    engine = build_engine(get_settings().sqlite_url)
    Base.metadata.create_all(bind=engine)
    return engine


@lru_cache
def _get_session_factory() -> sessionmaker[Session]:
    return get_session_factory(_get_engine())


def get_db_session() -> Generator[Session, None, None]:
    session = _get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_cache_backend() -> CacheBackend:
    return _cache_backend


def get_rate_limit_service() -> RateLimitService:
    return _rate_limit_service


def get_http_client() -> HttpClient:
    return _http_client


def get_hcm_service() -> HcmServicePort:
    return _hcm_service


def get_script_registry() -> ScriptRegistry:
    return _script_registry


def get_users_service(db_session: Session = Depends(get_db_session)) -> UsersService:
    return UsersService(UsersRepository(db_session))


def get_balances_service(db_session: Session = Depends(get_db_session)) -> BalancesService:
    return BalancesService(LeaveBalancesRepository(db_session))


def get_audit_service(db_session: Session = Depends(get_db_session)) -> AuditService:
    return AuditService(AuditEventsRepository(db_session))


def get_leaves_service(
    db_session: Session = Depends(get_db_session),
    hcm_service: HcmServicePort = Depends(get_hcm_service),
) -> LeavesService:
    return LeavesService(
        leave_requests_repository=LeaveRequestsRepository(db_session),
        hcm_service=hcm_service,
        policy_service=LeavePolicyService(),
        state_machine=LeaveStateMachine(),
        audit_service=AuditService(AuditEventsRepository(db_session)),
        users_service=UsersService(UsersRepository(db_session)),
    )


def get_reconciliation_service(
    db_session: Session = Depends(get_db_session),
    hcm_service: HcmServicePort = Depends(get_hcm_service),
) -> ReconciliationService:
    return ReconciliationService(
        leave_requests_repository=LeaveRequestsRepository(db_session),
        leave_balances_repository=LeaveBalancesRepository(db_session),
        users_repository=UsersRepository(db_session),
        hcm_service=hcm_service,
        state_machine=LeaveStateMachine(),
        audit_service=AuditService(AuditEventsRepository(db_session)),
    )


def get_scripts_service(
    db_session: Session = Depends(get_db_session),
    hcm_service: HcmServicePort = Depends(get_hcm_service),
) -> ScriptsService:
    registry = get_script_registry()
    reconciliation_service = get_reconciliation_service(db_session, hcm_service)
    registry.register(
        "sync_all_balances", lambda **_: sync_all_balances_script(reconciliation_service)
    )
    registry.register(
        "reconcile_recent_leaves",
        lambda **_: reconcile_recent_leaves_script(reconciliation_service),
    )
    registry.register(
        "backfill_balances", lambda **_: backfill_balances_script(reconciliation_service)
    )
    registry.register(
        "repair_pending_reconciliation",
        lambda **_: repair_pending_reconciliation_script(reconciliation_service),
    )
    return ScriptsService(ScriptRunsRepository(db_session), registry, LocalScriptRunner())
