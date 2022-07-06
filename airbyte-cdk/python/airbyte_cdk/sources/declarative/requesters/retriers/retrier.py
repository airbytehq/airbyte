#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

import requests


class NonRetriableResponseStatus(Enum):
    Ok = ("OK",)
    FAIL = ("FAIL",)
    IGNORE = ("IGNORE",)


@dataclass
class RetryResponseStatus:
    retry_in: Optional[float]


ResponseStatus = Union[NonRetriableResponseStatus, RetryResponseStatus]


class Retrier(ABC):
    @property
    @abstractmethod
    def max_retries(self) -> Union[int, None]:
        """
        Specifies maximum amount of retries for backoff policy. Return None for no limit.
        """
        pass

    @property
    @abstractmethod
    def retry_factor(self) -> float:
        """
        Override if needed. Specifies factor for exponential backoff policy. Not used for other backoff strategies.
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
