#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Union

import requests


class ResponseAction(Enum):
    """
    Response statuses for non retriable responses
    """

    SUCCESS = "SUCCESS"  # "Request was successful"
    FAIL = "FAIL"  # "Request failed unexpectedly"
    IGNORE = "IGNORE"  # "Request failed but can be ignored"
    RETRY = "RETRY"  # Request failed and should be retried


class ResponseStatus:
    def __init__(self, response_action: Union[ResponseAction, str], retry_in: Optional[float] = None):
        if isinstance(response_action, str):
            response_action = ResponseAction[response_action]
        if retry_in:
            assert response_action == ResponseAction.RETRY
        self._retry_in = retry_in
        self._action = response_action

    @property
    def action(self):
        return self._action

    @property
    def retry_in(self) -> Optional[float]:
        return self._retry_in

    @classmethod
    def success(cls):
        return ResponseStatus(ResponseAction.SUCCESS)

    @classmethod
    def fail(cls):
        return ResponseStatus(ResponseAction.FAIL)

    @classmethod
    def ignore(cls):
        return ResponseStatus(ResponseAction.IGNORE)

    @classmethod
    def retry(cls, retry_in: Optional[float]):
        return ResponseStatus(ResponseAction.RETRY, retry_in)

    def __eq__(self, other):
        if not other:
            return not self
        return self.action == other.action and self.retry_in == other.retry_in

    def __hash__(self):
        return hash([self.action, self.retry_in])


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
