#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests
from abc import ABC, abstractmethod
from typing import Optional
from .response_action import ResponseAction

class RetryStrategy(ABC):

    @property
    @abstractmethod
    def max_retries(self) -> int:
        """
        Override if needed. Specifies maximum amount of retries for backoff policy. Return None for no limit.
        """
        pass

    @property
    @abstractmethod
    def max_timeout(self) -> int:
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
    def should_retry(self, response: Optional[requests.Response] = None, response_action: Optional[ResponseAction] = None) -> bool:
        """
        Override to set different conditions for backoff based on the response from the server.

        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors

        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
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

    @abstractmethod
    def error_message(self, response: requests.Response) -> str:
        """
        Override this method to specify a custom error message which can incorporate the HTTP response received

        :param response: The incoming HTTP response from the API
        :return:
        """
        pass
