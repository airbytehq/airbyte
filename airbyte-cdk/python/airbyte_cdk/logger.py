#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import logging.config
from typing import Any, Mapping, Optional, Tuple

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "airbyte": {"()": "airbyte_cdk.logger.AirbyteLogFormatter", "format": "%(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "airbyte",
        },
    },
    "root": {
        "handlers": ["console"],
    },
}


def init_logger(name: Optional[str] = None) -> logging.Logger:
    """Initial set up of logger"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logging.config.dictConfig(LOGGING_CONFIG)
    return logger


class AirbyteLogFormatter(logging.Formatter):
    """Output log records using AirbyteMessage"""

    # Transforming Python log levels to Airbyte protocol log levels
    level_mapping = {
        logging.FATAL: "FATAL",
        logging.ERROR: "ERROR",
        logging.WARNING: "WARN",
        logging.INFO: "INFO",
        logging.DEBUG: "DEBUG",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Return a JSON representation of the log message"""
        airbyte_level = self.level_mapping.get(record.levelno, "INFO")
        if airbyte_level == "DEBUG":
            extras = self.extract_extra_args_from_record(record)
            debug_dict = {"type": "DEBUG", "message": record.getMessage(), "data": extras}
            return filter_secrets(json.dumps(debug_dict))
        else:
            message = super().format(record)
            message = filter_secrets(message)
            log_message = AirbyteMessage(type="LOG", log=AirbyteLogMessage(level=airbyte_level, message=message))
            return log_message.model_dump_json(exclude_unset=True)  # type: ignore

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
