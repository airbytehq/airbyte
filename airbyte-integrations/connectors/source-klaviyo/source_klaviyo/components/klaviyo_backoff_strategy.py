#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional, Union

import requests
from airbyte_cdk.sources.streams.http.error_handlers import DefaultBackoffStrategy
from source_klaviyo.exceptions import KlaviyoBackoffError


class KlaviyoBackoffStrategy(DefaultBackoffStrategy):
    def __init__(self, max_time: int, name: str) -> None:

        self._max_time = max_time
        self._name = name

    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs
    ) -> Optional[float]:

        if isinstance(response_or_exception, requests.Response):
            if response_or_exception.status_code == 429:
                retry_after = response_or_exception.headers.get("Retry-After")
                retry_after = float(retry_after) if retry_after else None
                if retry_after and retry_after >= self._max_time:
                    raise KlaviyoBackoffError(
                        f"Stream {self._name} has reached rate limit with 'Retry-After' of {retry_after} seconds, exit from stream."
                    )
                return float(retry_after) if retry_after else None
        return None
