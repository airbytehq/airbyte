# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from typing import Callable, Optional

import requests

from .response_action import ResponseAction


class DefaultRetryStrategy:
    def __init__(
        self,
        max_retries: int = 3,
        max_time: Optional[int] = 600,
        retry_factor: float = 5,
        raise_on_http_errors: bool = True,
        should_retry: Callable[[requests.Response], bool] = None,
        backoff_time: Callable[[requests.Response], Optional[float]] = None,
        error_message: Callable[[requests.Response], str] = None,
    ):

        self.max_retries = max_retries
        self.max_time = max_time
        self.retry_factor = retry_factor
        self.raise_on_http_errors = raise_on_http_errors

        self.should_retry = should_retry or self.should_retry
        self.backoff_time = backoff_time or self.backoff_time
        self.error_message = error_message or self.error_message

    def should_retry(self, response: Optional[requests.Response] = None, response_action: Optional[ResponseAction] = None) -> bool:

        if response_action:
            return response_action == ResponseAction.RETRY

        if response:
            return response.status_code == 429 or 500 <= response.status_code < 600

        return False

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.

        This method is called only if should_backoff() returns True for the input request.

        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return None

    def error_message(self, response: requests.Response) -> str:
        """
        Override this method to specify a custom error message which can incorporate the HTTP response received

        :param response: The incoming HTTP response from the API
        :return:
        """
        return ""
