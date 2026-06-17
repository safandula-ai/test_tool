from __future__ import annotations

import sys
from contextvars import ContextVar, Token
from pathlib import Path

from loguru import logger

from config.settings import ROOT


_TEST_LOG_BUFFER: ContextVar[list[str] | None] = ContextVar(
    "test_log_buffer",
    default=None,
)


def _capture_test_log(message) -> None:
    """Append loguru output to the active per-test in-memory buffer."""
    buffer = _TEST_LOG_BUFFER.get()
    if buffer is None:
        return
    buffer.append(str(message).rstrip("\n"))


def start_test_log_capture() -> tuple[list[str], Token[list[str] | None]]:
    """Start collecting log lines for the currently running pytest item."""
    buffer: list[str] = []
    token = _TEST_LOG_BUFFER.set(buffer)
    return buffer, token


def stop_test_log_capture(token: Token[list[str] | None]) -> None:
    """Restore the previous log-capture context after a test finishes."""
    _TEST_LOG_BUFFER.reset(token)


def get_logger(level: str = "INFO", log_file: str | Path | None = None):
    """Configure stdout, file, and per-test loguru sinks for the framework."""
    path = Path(log_file) if log_file is not None else ROOT / "logs" / "framework.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(
        sink=sys.stdout,
        level=level.upper(),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )
    logger.add(
        path,
        level=level.upper(),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8",
        enqueue=True,
    )
    logger.add(
        _capture_test_log,
        level=level.upper(),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        enqueue=False,
    )
    return logger
