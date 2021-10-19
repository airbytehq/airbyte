#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
import logging.config
import traceback

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage

TRACE_LEVEL_NUM = 5

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


def init_logger(name: str = None):
    """Initial set up of logger"""
    logging.setLoggerClass(AirbyteNativeLogger)
    logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
    logger = logging.getLogger(name)
    logger.setLevel(TRACE_LEVEL_NUM)
    logging.config.dictConfig(LOGGING_CONFIG)
    return logger


class AirbyteLogFormatter(logging.Formatter):
    """Output log records using AirbyteMessage"""

    def format(self, record: logging.LogRecord) -> str:
        """Return a JSON representation of the log message"""
        message = super().format(record)
        log_message = AirbyteMessage(type="LOG", log=AirbyteLogMessage(level=record.levelname, message=message))
        return log_message.json(exclude_unset=True)


class AirbyteNativeLogger(logging.Logger):
    """Using native logger with implementing all AirbyteLogger features"""

    def __init__(self, name):
        super().__init__(name)
        self.valid_log_types = ["FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"]

    def log_by_prefix(self, msg, default_level):
        """Custom method, which takes log level from first word of message"""
        split_line = msg.split()
        first_word = next(iter(split_line), None)
        if first_word in self.valid_log_types:
            log_level = logging.getLevelName(first_word)
            rendered_message = " ".join(split_line[1:])
        else:
            default_level = default_level if default_level in self.valid_log_types else "INFO"
            log_level = logging.getLevelName(default_level)
            rendered_message = msg
        self.log(log_level, rendered_message)

    def trace(self, msg, *args, **kwargs):
        self._log(TRACE_LEVEL_NUM, msg, args, **kwargs)


class AirbyteLogger:
    def __init__(self):
        self.valid_log_types = ["FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"]

    def log_by_prefix(self, message, default_level):
        """Custom method, which takes log level from first word of message"""
        split_line = message.split()
        first_word = next(iter(split_line), None)
        if first_word in self.valid_log_types:
            log_level = first_word
            rendered_message = " ".join(split_line[1:])
        else:
            log_level = default_level
            rendered_message = message
        self.log(log_level, rendered_message)

    def log(self, level, message):
        log_record = AirbyteLogMessage(level=level, message=message)
        log_message = AirbyteMessage(type="LOG", log=log_record)
        print(log_message.json(exclude_unset=True))

    def fatal(self, message):
        self.log("FATAL", message)

    def exception(self, message):
        message = f"{message}\n{traceback.format_exc()}"
        self.error(message)

    def error(self, message):
        self.log("ERROR", message)

    def warn(self, message):
        self.log("WARN", message)

    def info(self, message):
        self.log("INFO", message)

    def debug(self, message):
        self.log("DEBUG", message)

    def trace(self, message):
        self.log("TRACE", message)
