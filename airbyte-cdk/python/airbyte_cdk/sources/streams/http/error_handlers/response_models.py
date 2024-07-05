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
