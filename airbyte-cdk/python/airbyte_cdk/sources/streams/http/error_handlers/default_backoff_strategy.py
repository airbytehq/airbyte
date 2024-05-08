# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from typing import Optional, Union

import requests

from .backoff_strategy import BackoffStrategy


class DefaultBackoffStrategy(BackoffStrategy):
    def __init__(
        self,
        max_retries: int = 5,
        max_time: int = 60 * 10,
    ):
        self.max_retries = max_retries
        self.max_time = max_time

    def backoff_time(self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]]) -> Optional[float]:
        """
        Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.

        This method is called only if should_backoff() returns True for the input request.

        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return None
