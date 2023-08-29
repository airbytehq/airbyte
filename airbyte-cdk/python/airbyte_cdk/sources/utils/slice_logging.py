#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, Mapping, Optional

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level
from airbyte_cdk.models import Type as MessageType

SLICE_LOG_PREFIX = "slice:"


def create_slice_log_message(_slice: Optional[Mapping[str, Any]]) -> AirbyteMessage:
    """
    Mapping is an interface that can be implemented in various ways. However, json.dumps will just do a `str(<object>)` if
    the slice is a class implementing Mapping. Therefore, we want to cast this as a dict before passing this to json.dump
    """
    printable_slice = dict(_slice) if _slice else _slice
    return AirbyteMessage(
        type=MessageType.LOG,
        log=AirbyteLogMessage(level=Level.INFO, message=f"{SLICE_LOG_PREFIX}{json.dumps(printable_slice, default=str)}"),
    )


def should_log_slice_message(logger: logging.Logger) -> bool:
    """

    :param logger:
    :return:
    """
    return logger.isEnabledFor(logging.DEBUG)
