#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
import logging.config
from functools import reduce
from typing import Mapping, Optional

from airbyte_cdk.sources import Source

from .logger import LOGGING_CONFIG, TRACE_LEVEL_NUM, AirbyteLogFormatter, AirbyteNativeLogger


def init_secure_logger(name: str = None, source: Optional[Source] = None, config: Optional[Mapping] = None):
    """Initial set up of logger"""
    logging.setLoggerClass(AirbyteNativeLogger)
    logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
    logger = logging.getLogger(name)

    logger.setLevel(TRACE_LEVEL_NUM)
    logging.config.dictConfig(LOGGING_CONFIG)
    for handler in logger.handlers:
        handler.setFormatter(AirbyteSecureLogFormatter(source, config))

    return logger


class AirbyteSecureLogFormatter(AirbyteLogFormatter):
    def __init__(
        self,
        fmt: Optional[str] = ...,
        datefmt: Optional[str] = ...,
        style: str = ...,
        validate: bool = ...,
        source: Source = None,
        config: Mapping = None,
    ) -> None:
        super().__init__(fmt, datefmt, style, validate)
        if source and config:
            self.secrets_strings = self.get_secrets(source, config)
        else:
            self.secrets_strings = []

    def format(self, record: logging.LogRecord) -> str:
        reduce(lambda log_msg, secret: log_msg.replace(secret, "****"), self.secrets_strings, record.msg)
        return super(AirbyteSecureLogFormatter, self).format(record)

    @staticmethod
    def get_secrets(source, config):
        secret_key_names = [k for k, v in source.spec().connectionSpecification["properties"].items() if v.get("airbyte_secret", False)]
        return [config.get(k) for k in secret_key_names if config.get(k)]
