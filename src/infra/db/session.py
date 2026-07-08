from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


def build_engine(sqlite_url: str) -> Engine:
    connect_args = {"check_same_thread": False} if sqlite_url.startswith("sqlite") else {}
    if ":memory:" in sqlite_url:
        return create_engine(
            sqlite_url, future=True, connect_args=connect_args, poolclass=StaticPool
        )
    return create_engine(sqlite_url, future=True, connect_args=connect_args)


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db_session(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()