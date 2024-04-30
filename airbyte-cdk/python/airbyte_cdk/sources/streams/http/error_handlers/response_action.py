# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from enum import Enum


class ResponseAction(Enum):

    SUCCESS = "SUCCESS"
    RETRY = "RETRY"
    FAIL = "FAIL"
    IGNORE = "IGNORE"
