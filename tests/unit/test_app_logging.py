# Tests for application logging configuration.
# Validates log level configuration and named logger retrieval.

from __future__ import annotations

import logging

from src.app.logging import configure_logging, get_logger


# configure_logging sets root logger level to DEBUG
def test_configure_logging_sets_level() -> None:
    configure_logging("DEBUG")
    assert logging.getLogger().level == logging.DEBUG


# get_logger returns a logger with the specified name
def test_get_logger_returns_named_logger() -> None:
    logger = get_logger("my.module")
    assert logger.name == "my.module"
