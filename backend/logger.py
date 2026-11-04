import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "ola_agent.log"

logger = logging.getLogger("ola_agent")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        "[%(asctime)s] [Ola] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)


def log_agent_event(
    event_type: str,
    thread_id: str,
    message: str,
    details: Optional[dict[str, Any]] = None
) -> None:
    """Log an agent event with thread ID and optional details."""
    detail_str = ""
    if details:
        cleaned_details = {}
        for k, v in details.items():
            if isinstance(v, str) and len(v) > 200:
                cleaned_details[k] = v[:200] + "... (truncated)"
            elif isinstance(v, list) and len(v) > 5:
                cleaned_details[k] = v[:5] + [f"... and {len(v)-5} more"]
            else:
                cleaned_details[k] = v
        detail_str = f" | {cleaned_details}"

    logger.info(f"[{thread_id}] [{event_type.upper()}] {message}{detail_str}")


def log_agent_error(
    thread_id: str,
    message: str,
    error: Optional[Exception] = None
) -> None:
    """Log an agent error or exception."""
    err_str = f" | Exception: {str(error)}" if error else ""
    logger.error(f"[{thread_id}] [ERROR] {message}{err_str}")
