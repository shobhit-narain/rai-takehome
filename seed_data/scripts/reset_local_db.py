#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


def sqlite_path_from_url(sqlite_url: str) -> Path | None:
    prefix = "sqlite:///"
    if not sqlite_url.startswith(prefix):
        return None

    raw_path = sqlite_url[len(prefix):]
    if raw_path == ":memory:":
        return None

    return Path(raw_path).resolve()


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        from src.infra.db.base import Base
        from src.infra.db.session import build_engine
        from src.app.config import AppSettings
    except ImportError as exc:
        print(f"Import error: {exc}")
        print("Make sure dependencies are installed and the project structure is in place.")
        return 1

    settings = AppSettings()
    engine = build_engine(settings.sqlite_url)

    db_path = sqlite_path_from_url(settings.sqlite_url)
    if db_path and db_path.exists():
        db_path.unlink()
        print(f"Removed existing database file: {db_path}")

    Base.metadata.create_all(bind=engine)
    print("Local database reset successfully.")
    print(f"SQLite URL: {settings.sqlite_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())