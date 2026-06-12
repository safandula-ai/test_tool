from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger


def get_logger(level: str = "INFO", log_file: str | Path = "logs/framework.log"):
    path = Path(log_file)
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
    return logger
