#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import logging
import logging.config
import os
from typing import Any, Callable, Mapping, Optional, Tuple

import orjson

from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteMessageSerializer,
    Level,
    Type,
)
from airbyte_cdk.utils import PrintBuffer
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets

PRINT_BUFFER = PrintBuffer(flush_interval=0.1)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "airbyte": {"()": "airbyte_cdk.logger.AirbyteLogFormatter", "format": "%(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": PRINT_BUFFER,
            "formatter": "airbyte",
        },
    },
    "root": {
        "handlers": ["console"],
    },
}


def is_platform_debug_log_enabled() -> bool:
    return os.environ.get("LOG_LEVEL", "info").lower() == "debug"


def init_logger(name: Optional[str] = None) -> logging.Logger:
    """Initial set up of logger"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logging.config.dictConfig(LOGGING_CONFIG)
    return logger


def lazy_log(logger: logging.Logger, level: int, lazy_log_provider: Callable[[], str]) -> None:
    """
    This method ensure that the processing of the log message is only done if the logger is enabled for the log level.
    """
    if logger.isEnabledFor(level):
        logger.log(level, lazy_log_provider())


class AirbyteLogFormatter(logging.Formatter):
    """Output log records using AirbyteMessage"""

    # Transforming Python log levels to Airbyte protocol log levels
    level_mapping = {
        logging.FATAL: Level.FATAL,
        logging.ERROR: Level.ERROR,
        logging.WARNING: Level.WARN,
        logging.INFO: Level.INFO,
        logging.DEBUG: Level.DEBUG,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Return a JSON representation of the log message"""
        airbyte_level = self.level_mapping.get(record.levelno, "INFO")
        if airbyte_level == Level.DEBUG:
            extras = self.extract_extra_args_from_record(record)
            if is_platform_debug_log_enabled():
                # We have a different behavior between debug logs enabled through `--debug` argument and debug logs
                # enabled through environment variable. The reason is that for platform logs, we need to have these
                # printed as AirbyteMessage which is not the case with the current previous implementation.
                # Why not migrate both to AirbyteMessages then? AirbyteMessages do not support having structured logs.
                # which means that the DX would be degraded compared to the current solution (devs will need to identify
                # the `log.message` field and figure out where in this field is the response while the current solution
                # have a specific field that is structured for extras.
                message = f"{filter_secrets(record.getMessage())} ///\nExtra logs: {filter_secrets(json.dumps(extras))}"
                log_message = AirbyteMessage(
                    type=Type.LOG, log=AirbyteLogMessage(level=airbyte_level, message=message)
                )
                return orjson.dumps(AirbyteMessageSerializer.dump(log_message)).decode()
            else:
                debug_dict = {"type": "DEBUG", "message": record.getMessage(), "data": extras}
                return filter_secrets(json.dumps(debug_dict))
        else:
            message = super().format(record)
            message = filter_secrets(message)
            log_message = AirbyteMessage(
                type=Type.LOG, log=AirbyteLogMessage(level=airbyte_level, message=message)
            )
            return orjson.dumps(AirbyteMessageSerializer.dump(log_message)).decode()

    @staticmethod
    def extract_extra_args_from_record(record: logging.LogRecord) -> Mapping[str, Any]:
        """
        The python logger conflates default args with extra args. We use an empty log record and set operations
        to isolate fields passed to the log record via extra by the developer.
        """
        default_attrs = logging.LogRecord("", 0, "", 0, None, None, None).__dict__.keys()
        extra_keys = set(record.__dict__.keys()) - default_attrs
        return {k: str(getattr(record, k)) for k in extra_keys if hasattr(record, k)}


def log_by_prefix(msg: str, default_level: str) -> Tuple[int, str]:
    """Custom method, which takes log level from first word of message"""
    valid_log_types = ["FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"]
    split_line = msg.split()
    first_word = next(iter(split_line), None)
    if first_word in valid_log_types:
        log_level = logging.getLevelName(first_word)
        rendered_message = " ".join(split_line[1:])
    else:
        log_level = logging.getLevelName(default_level)
        rendered_message = msg

    return log_level, rendered_message
