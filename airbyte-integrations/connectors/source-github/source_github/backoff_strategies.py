#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time
from typing import Any, Optional, Union

import requests

from airbyte_cdk import BackoffStrategy
from airbyte_cdk.sources.streams.http import HttpStream


class GithubStreamABCBackoffStrategy(BackoffStrategy):
    def __init__(self, stream: HttpStream, **kwargs):  # type: ignore # noqa
        self.stream = stream
        super().__init__(**kwargs)

    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        # This method is called if we run into the rate limit. GitHub limits requests to 5000 per hour and provides
        # `X-RateLimit-Reset` header which contains time when this hour will be finished and limits will be reset so
        # we again could have 5000 per another hour.
        #
        # The wait returned here is only paid when no other token can serve the request. The
        # shared RateLimitedMultipleTokenAuthenticator zeroes the rejected token's quota pool
        # from the response headers, and `HttpClient` asks it (`has_alternative_token`) before
        # sleeping on a rate limit, retrying on a spare token in 0.1s instead. That replaces the
        # connector-side rotation this strategy used to do at the 10-minute mark, and gives the
        # Python and manifest streams one shared implementation.
        if isinstance(response_or_exception, requests.Response):
            min_backoff_time = 60.0
            retry_after = response_or_exception.headers.get("Retry-After")
            if retry_after is not None:
                return max(float(retry_after), min_backoff_time)

            reset_time = response_or_exception.headers.get("X-RateLimit-Reset")
            if reset_time:
                return max(float(reset_time) - time.time(), min_backoff_time)
        return None


class ContributorActivityBackoffStrategy(BackoffStrategy):
    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == requests.codes.ACCEPTED:
            return 90
        return None
