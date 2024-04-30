#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Optional

import requests


class BackoffStrategy(ABC):
    @property
    @abstractmethod
    def max_retries(self) -> int:
        """
        Override if needed. Specifies maximum amount of retries for backoff policy. Return None for no limit.
        """
        pass

    @property
    @abstractmethod
    def max_time(self) -> int:
        """
        Override if needed. Specifies maximum total waiting time (in seconds) for backoff policy. Return None for no limit.
        """
        pass

    @property
    @abstractmethod
    def retry_factor(self) -> float:
        """
        Override if needed. Specifies factor for backoff policy.
        """
        pass

    @abstractmethod
    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.

        This method is called only if should_backoff() returns True for the input request.

        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        pass
