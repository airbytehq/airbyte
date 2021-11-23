#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
import logging.config
from functools import reduce
from typing import Mapping, Optional

from airbyte_cdk.sources import Source

from .logger import LOGGING_CONFIG, TRACE_LEVEL_NUM, AirbyteNativeLogger


def init_secure_logger(name: str = None, source: Optional[Source] = None, config: Optional[Mapping] = None):
    """Initial set up of logger"""
    logging.setLoggerClass(AirbyteNativeLogger)
    logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
    logger = logging.getLogger(name)
    logger.propagate = True

    logger.setLevel(TRACE_LEVEL_NUM)
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.addFilter(AirbyteLogFilter(source, config))
    return logger


class AirbyteLogFilter(logging.Filter):
    def __init__(self, source: Optional[Source] = None, config: Optional[Mapping] = None):
        super().__init__()
        if source and config:
            self.secrets_strings = self.get_secrets(source, config)
        else:
            self.secrets_strings = []

    def filter(self, record: logging.LogRecord) -> str:
        record.msg = reduce(
            lambda log_msg, secret: log_msg.replace(secret, "****"),
            self.secrets_strings,
            record.msg,
        )
        return True

    @staticmethod
    def get_secrets(source, config):
        secret_key_names = [
            k for k, v in source.spec().connectionSpecification.get("properties", {}).items() if v.get("airbyte_secret", False)
        ]
        return [str(config.get(k)) for k in secret_key_names if config.get(k)]
