#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from enum import Enum


class ResponseAction(Enum):
    """
    Response statuses for non retriable responses
    """

    SUCCESS = "SUCCESS"  # "Request was successful"
    FAIL = "FAIL"  # "Request failed unexpectedly"
    IGNORE = "IGNORE"  # "Request failed but can be ignored"
    RETRY = "RETRY"  # Request failed and should be retried
