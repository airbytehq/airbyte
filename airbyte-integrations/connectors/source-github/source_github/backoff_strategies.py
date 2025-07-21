#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time
from typing import Any, Optional, Union

import requests

from airbyte_cdk import BackoffStrategy
from airbyte_cdk.sources.streams.http import HttpStream


class GithubStreamABCBackoffStrategy(BackoffStrategy):
    min_backoff_time = 60.0
    # https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api?apiVersion=2022-11-28
    RATE_LIMITS_STATUS_CODES = [403, 429]

    def __init__(self, stream: HttpStream, **kwargs):  # type: ignore # noqa
        self.stream = stream
        super().__init__(**kwargs)

    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        # This method is called if we run into the rate limit. GitHub limits requests to 5000 per hour and provides
        # `X-RateLimit-Reset` header which contains time when this hour will be finished and limits will be reset so
        # we again could have 5000 per another hour.
        if isinstance(response_or_exception, requests.Response):
            retry_after = response_or_exception.headers.get("Retry-After")
            if retry_after is not None:
                backoff_time_in_seconds = max(float(retry_after), self.min_backoff_time)
                return self.get_waiting_time(backoff_time_in_seconds, response_or_exception)

            reset_time = response_or_exception.headers.get("X-RateLimit-Reset")
            if reset_time:
                backoff_time_in_seconds = max(float(reset_time) - time.time(), self.min_backoff_time)
                return self.get_waiting_time(backoff_time_in_seconds, response_or_exception)
        return None

    def get_waiting_time(self, backoff_time_in_seconds: float, response: requests.Response) -> Optional[float]:
        if backoff_time_in_seconds < 60 * 10:  # type: ignore[operator]
            return backoff_time_in_seconds
        else:
            # New token will be used in the next request or fail if all tokens are exhausted
            if response.status_code in self.RATE_LIMITS_STATUS_CODES:
                self.stream._http_client._session.auth.find_available_token(response.request)
            else:
                self.stream._http_client._session.auth.update_token()

            # update headers in the request itself so the next request will use new token
            response.request.headers.update(self.stream._http_client._session.auth.get_auth_header())

            return 1


class ContributorActivityBackoffStrategy(BackoffStrategy):
    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == requests.codes.ACCEPTED:
            return 90
        return None
