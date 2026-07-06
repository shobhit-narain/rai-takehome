from __future__ import annotations

import logging

from src.app.logging import configure_logging, get_logger


def test_configure_logging_sets_level() -> None:
    configure_logging("DEBUG")
    assert logging.getLogger().level == logging.DEBUG


def test_get_logger_returns_named_logger() -> None:
    logger = get_logger("my.module")
    assert logger.name == "my.module"
