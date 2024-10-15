# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""PyAirbyte Logging features and related configuration.

By default, PyAirbyte main logs are written to a file in the `AIRBYTE_LOGGING_ROOT` directory, which
defaults to a system-created temporary directory. PyAirbyte also maintains connector-specific log
files within the same directory, under a subfolder with the name of the connector.

PyAirbyte supports structured JSON logging, which is disabled by default. To enable structured
logging in JSON, set `AIRBYTE_STRUCTURED_LOGGING` to `True`.
"""

from __future__ import annotations

import logging
import os
import platform
import tempfile
import warnings
from functools import lru_cache
from pathlib import Path

import pendulum
import structlog
import ulid


def _str_to_bool(value: str) -> bool:
    """Convert a string value of an environment values to a boolean value."""
    return bool(value) and value.lower() not in {"", "0", "false", "f", "no", "n", "off"}


AIRBYTE_STRUCTURED_LOGGING: bool = _str_to_bool(
    os.getenv(
        key="AIRBYTE_STRUCTURED_LOGGING",
        default="false",
    )
)
"""Whether to enable structured logging.

This value is read from the `AIRBYTE_STRUCTURED_LOGGING` environment variable. If the variable is
not set, the default value is `False`.
"""

_warned_messages: set[str] = set()


def warn_once(
    message: str,
    logger: logging.Logger | None = None,
    *,
    with_stack: int | bool,
) -> None:
    """Emit a warning message only once.

    This function is a wrapper around the `warnings.warn` function that logs the warning message
    to the global logger. The warning message is only emitted once per unique message.
    """
    if message in _warned_messages:
        return

    if not with_stack:
        stacklevel = 0
    if with_stack is True:
        stacklevel = 2

    _warned_messages.add(message)
    warnings.warn(
        message,
        category=UserWarning,
        stacklevel=stacklevel,
    )

    if logger:
        logger.warning(message)


def _get_logging_root() -> Path | None:
    """Return the root directory for logs.

    Returns `None` if no valid path can be found.

    This is the directory where logs are stored.
    """
    if "AIRBYTE_LOGGING_ROOT" in os.environ:
        log_root = Path(os.environ["AIRBYTE_LOGGING_ROOT"])
    elif platform.system() == "Darwin" or platform.system() == "Linux":
        # Use /tmp on macOS and Linux
        log_root = Path("/tmp") / "airbyte" / "logs"
    else:
        # Use the default temp directory on Windows or any other OS
        log_root = Path(tempfile.gettempdir()) / "airbyte" / "logs"

    try:
        # Attempt to create the log root directory if it does not exist
        log_root.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Handle the error by returning None
        warn_once(
            (
                f"Failed to create PyAirbyte logging directory at `{log_root}`. "
                "You can override the default path by setting the `AIRBYTE_LOGGING_ROOT` "
                "environment variable."
            ),
            with_stack=False,
        )
        return None
    else:
        return log_root


AIRBYTE_LOGGING_ROOT: Path | None = _get_logging_root()
"""The root directory for Airbyte logs.

This value can be overridden by setting the `AIRBYTE_LOGGING_ROOT` environment variable.

If not provided, PyAirbyte will use `/tmp/airbyte/logs/` where `/tmp/` is the OS's default
temporary directory. If the directory cannot be created, PyAirbyte will log a warning and
set this value to `None`.
"""


@lru_cache
def get_global_file_logger() -> logging.Logger | None:
    """Return the global logger for PyAirbyte.

    This logger is configured to write logs to the console and to a file in the log directory.
    """
    logger = logging.getLogger("airbyte")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if AIRBYTE_LOGGING_ROOT is None:
        # No temp directory available, so return None
        return None

    # Else, configure the logger to write to a file

    # Remove any existing handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)

    yyyy_mm_dd: str = pendulum.now().format("YYYY-MM-DD")
    folder = AIRBYTE_LOGGING_ROOT / yyyy_mm_dd
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except Exception:
        warn_once(
            f"Failed to create logging directory at '{folder!s}'.",
            with_stack=False,
        )
        return None

    logfile_path = folder / f"airbyte-log-{str(ulid.ULID())[2:11]}.log"
    print(f"Writing PyAirbyte logs to file: {logfile_path!s}")

    file_handler = logging.FileHandler(
        filename=logfile_path,
        encoding="utf-8",
    )

    if AIRBYTE_STRUCTURED_LOGGING:
        # Create a formatter and set it for the handler
        formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)

        # Configure structlog
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Create a logger
        return structlog.get_logger("airbyte")

    # Create and configure file handler
    file_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    logger.addHandler(file_handler)
    return logger


def get_global_stats_log_path() -> Path | None:
    """Return the path to the performance log file."""
    if AIRBYTE_LOGGING_ROOT is None:
        return None

    folder = AIRBYTE_LOGGING_ROOT
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except Exception:
        warn_once(
            f"Failed to create logging directory at '{folder!s}'.",
            with_stack=False,
        )
        return None

    return folder / "airbyte-stats.log"


@lru_cache
def get_global_stats_logger() -> structlog.BoundLogger:
    """Create a stats logger for performance metrics."""
    logger = logging.getLogger("airbyte.stats")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logfile_path: Path | None = get_global_stats_log_path()
    if AIRBYTE_LOGGING_ROOT is None or logfile_path is None:
        # No temp directory available, so return no-op logger without handlers
        return structlog.get_logger("airbyte.stats")

    print(f"Writing PyAirbyte performance stats to file: {logfile_path!s}")

    # Remove any existing handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)

    folder = AIRBYTE_LOGGING_ROOT
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except Exception:
        warn_once(
            f"Failed to create logging directory at '{folder!s}'.",
            with_stack=False,
        )
        return structlog.get_logger("airbyte.stats")

    file_handler = logging.FileHandler(
        filename=logfile_path,
        encoding="utf-8",
    )

    # Create a formatter and set it for the handler
    formatter = logging.Formatter("%(message)s")
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Create a logger
    return structlog.get_logger("airbyte.stats")


def new_passthrough_file_logger(connector_name: str) -> logging.Logger:
    """Create a logger from logging module."""
    logger = logging.getLogger(f"airbyte.{connector_name}")
    logger.setLevel(logging.INFO)

    # Prevent logging to stderr by stopping propagation to the root logger
    logger.propagate = False

    if AIRBYTE_LOGGING_ROOT is None:
        # No temp directory available, so return a basic logger
        return logger

    # Else, configure the logger to write to a file

    # Remove any existing handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)

    folder = AIRBYTE_LOGGING_ROOT / connector_name
    folder.mkdir(parents=True, exist_ok=True)

    # Create a file handler
    global_logger = get_global_file_logger()
    logfile_path = folder / f"{connector_name}-log-{str(ulid.ULID())[2:11]}.log"
    logfile_msg = f"Writing `{connector_name}` logs to file: {logfile_path!s}"
    print(logfile_msg)
    if global_logger:
        global_logger.info(logfile_msg)

    file_handler = logging.FileHandler(logfile_path)
    file_handler.setLevel(logging.INFO)

    if AIRBYTE_STRUCTURED_LOGGING:
        # Create a formatter and set it for the handler
        formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)

        # Configure structlog
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Create a logger
        return structlog.get_logger(f"airbyte.{connector_name}")

    # Else, write logs in plain text

    file_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    logger.addHandler(file_handler)
    return logger
