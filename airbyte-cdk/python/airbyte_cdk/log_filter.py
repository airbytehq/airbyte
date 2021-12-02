#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
import logging.config
import sys
from functools import reduce, partial
from typing import Optional, List, Any

from .logger import LOGGING_CONFIG, TRACE_LEVEL_NUM, AirbyteNativeLogger


def init_filtered_logger(name: str = None, secrets: List[Any] = []) -> logging.Logger:
    """Initial set up of logger"""
    logging.setLoggerClass(AirbyteNativeLogger)
    logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
    logger = logging.getLogger(name)
    logger.propagate = True

    logger.setLevel(TRACE_LEVEL_NUM)
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.addFilter(AirbyteLogFilter(secrets))
    return logger


def init_unhandled_exception_output_filtering(logger: logging.Logger) -> None:

    def hook_fn(_logger, exception_type, exception_value, traceback):
        # For developer ergonomics, we want to see the stack trace in the logs when we do a ctrl-c
        if issubclass(exception_type, KeyboardInterrupt):
            sys.__excepthook__(exception_type, exception_value, traceback)
            return

        logger.critical(str(exception_value), exc_info=(exception_type, Exception(), traceback))

    sys.excepthook = partial(hook_fn, logger)


class AirbyteLogFilter(logging.Filter):
    def __init__(self, secrets: List[Any]):
        super().__init__()
        self.secrets = secrets

    def filter(self, record: logging.LogRecord) -> str:
        record.msg = reduce(
            lambda log_msg, secret: log_msg.replace(str(secret), "****"),
            self.secrets,
            record.msg,
        )
        return True
