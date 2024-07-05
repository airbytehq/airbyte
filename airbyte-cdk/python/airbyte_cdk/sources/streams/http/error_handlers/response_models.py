# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from airbyte_cdk.models import FailureType


class ResponseAction(Enum):
    SUCCESS = "SUCCESS"
    RETRY = "RETRY"
    FAIL = "FAIL"
    IGNORE = "IGNORE"


@dataclass
class ErrorResolution:
    response_action: Optional[ResponseAction] = None
    failure_type: Optional[FailureType] = None
    error_message: Optional[str] = None


DEFAULT_ERROR_RESOLUTION = ErrorResolution(
    response_action=ResponseAction.RETRY,
    failure_type=FailureType.system_error,
    error_message="The request failed due to an unknown error.",
)

SUCCESS_RESOLUTION = ErrorResolution(response_action=ResponseAction.SUCCESS, failure_type=None, error_message=None)
