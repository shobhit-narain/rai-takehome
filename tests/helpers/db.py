from __future__ import annotations

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.infra.db.base import Base
from src.infra.db.seed import SeedService
from src.infra.db.session import build_engine


def create_test_db() -> Engine:
    engine = build_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine


def reset_test_db(engine: Engine) -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed_test_db(session_factory: sessionmaker[Session], data_dir: str | None = None) -> None:
    SeedService(session_factory, data_dir=data_dir).seed_all()
