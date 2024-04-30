# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from typing import Callable, Optional

import requests

from .backoff_strategy import BackoffStrategy


class DefaultBackoffStrategy(BackoffStrategy):
    def __init__(
        self,
        max_retries: int = 5,
        max_time: Optional[int] = 60 * 10,
        retry_factor: float = 5,
        raise_on_http_errors: bool = True,
        backoff_time: Callable[[requests.Response], Optional[float]] = None,
    ):

        self._max_retries = max_retries
        self._max_time = max_time
        self._retry_factor = retry_factor
        self._raise_on_http_errors = raise_on_http_errors
        self.backoff_time = backoff_time or self.backoff_time

    @property
    def max_retries(self) -> int:
        return self._max_retries

    @property
    def max_time(self) -> int:
        return self._max_time

    @property
    def retry_factor(self) -> float:
        return self._retry_factor

    @property
    def raise_on_http_errors(self) -> bool:
        return self._raise_on_http_errors

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.

        This method is called only if should_backoff() returns True for the input request.

        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return None
