#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Union

import requests


class NonRetriableResponseStatus(Enum):
    """
    Response statuses for non retriable responses
    """

    SUCCESS = "SUCCESS"  # "Request was successful"
    FAIL = "FAIL"  # "Request failed unexpectedly"
    IGNORE = "IGNORE"  # "Request failed but can be ignored"


@dataclass
class RetryResponseStatus:
    """
    Response status for request to be retried

    Attributes:
        retry_in: time to wait (in seconds) before retrying the request
    """

    retry_in: float


ResponseStatus = Union[NonRetriableResponseStatus, RetryResponseStatus]


class ErrorHandler(ABC):
    @property
    @abstractmethod
    def max_retries(self) -> Union[int, None]:
        """
        Specifies maximum amount of retries for backoff policy. Return None for no limit.
        """
        pass

    @abstractmethod
    def should_retry(self, response: requests.Response) -> ResponseStatus:
        """
        Evaluate response status describing whether a failing request should be retried or ignored.
        :param response: response to evaluate
        :return: response status
        """
        pass
