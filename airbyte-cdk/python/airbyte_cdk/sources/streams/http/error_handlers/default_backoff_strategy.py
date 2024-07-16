# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from typing import Any, Optional, Union

import requests

from .backoff_strategy import BackoffStrategy


class DefaultBackoffStrategy(BackoffStrategy):
    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        """
        Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.

        :param response_or_exception: The response or exception that caused the backoff.
        :param kwargs: Additional arguments that may be passed to the backoff strategy. Most commonly the attempt_count of the request.
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return None
