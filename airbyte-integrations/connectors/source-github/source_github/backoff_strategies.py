#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time
from typing import Any, Optional, Union

import requests

from airbyte_cdk import BackoffStrategy
from airbyte_cdk.sources.streams.http import HttpStream

from .errors_handlers import is_rate_limited_response


class GithubStreamABCBackoffStrategy(BackoffStrategy):
    def __init__(self, stream: HttpStream, max_wait_time_seconds: float = 120 * 60, **kwargs):  # type: ignore # noqa
        self.stream = stream
        self.max_wait_time_seconds = max_wait_time_seconds
        super().__init__(**kwargs)

    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        if isinstance(response_or_exception, requests.Response):
            if not is_rate_limited_response(
                response_or_exception,
                self.stream.check_graphql_rate_limited,
                self.stream.logger,
            ):
                return None

            min_backoff_time = 60.0
            retry_after = response_or_exception.headers.get("Retry-After")
            if retry_after is not None:
                wait_time = max(float(retry_after), min_backoff_time)
            else:
                reset_time = response_or_exception.headers.get("X-RateLimit-Reset")
                if not reset_time:
                    return None
                wait_time = max(float(reset_time) - time.time(), min_backoff_time)

            if wait_time > self.max_wait_time_seconds:
                self.stream.logger.warning(
                    "Rate limit wait for stream `%s` is %.2f seconds, exceeding the maximum of %.2f seconds; using default backoff.",
                    self.stream.name,
                    wait_time,
                    self.max_wait_time_seconds,
                )
                return None
            return wait_time
        return None


class ContributorActivityBackoffStrategy(BackoffStrategy):
    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == requests.codes.ACCEPTED:
            return 90
        return None
