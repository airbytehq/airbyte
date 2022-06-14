#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional, Union

import requests
from airbyte_cdk.sources.declarative.requesters.retriers.retrier import NonRetriableBehavior, Retrier, RetryBehavior


class HttpResponseFilter:
    def __init__(self, http_codes, error_message_contains=None, predicate=None):
        if isinstance(http_codes, int):
            http_codes = set([http_codes])
        self.http_codes = http_codes

    def matches(self, response) -> bool:
        # this is only a partial implementation. Also need to check the other fields...
        if response.status_code in self.http_codes:
            return True
        return False


DEFAULT_RETRIES = HttpResponseFilter(set(range(500, 600)))
DEFAULT_RETRIES.http_codes.add(429)


class BackoffStrategy:
    pass


class ConstantBackoff:
    def __init__(self, backoff_in_seconds):
        self._backoff_in_seconds = backoff_in_seconds

    def backoff(self, response):
        return self._backoff_in_seconds


class DefaultRetrier(Retrier):
    def __init__(
        self,
        max_retries: Optional[int] = 5,
        retry_factor: float = 5,
        ignore: List[HttpResponseFilter] = None,
        retry: List[HttpResponseFilter] = DEFAULT_RETRIES,
        backoff=None,
    ):
        if ignore is None:
            ignore = []
        if not isinstance(retry, list):
            retry = [retry]
        if backoff is None:
            backoff = []
        if not isinstance(backoff, list):
            backoff = [backoff]
        self._max_retries = max_retries
        self._retry_factor = retry_factor
        self.ignore = ignore
        self.retry: List[HttpResponseFilter] = retry
        self._backoff_strategies = backoff

    @property
    def max_retries(self) -> Union[int, None]:
        return self._max_retries

    @property
    def retry_factor(self) -> float:
        return self._retry_factor

    def should_retry(self, response: requests.Response) -> RetryBehavior:
        """
        1. If the retry, retry
        2. Else if ignore, ignore
        3. else if error, fail
        4. else: OK!
        """
        for retry_filter in self.retry:
            if retry_filter.matches(response):
                return self.backoff_time(response)
        ignore = False
        for ignore_filters in self.ignore:
            if ignore_filters.matches(response):
                ignore = True
        if ignore:
            return NonRetriableBehavior.Ignore
        if response.status_code == 200:
            return NonRetriableBehavior.Ok
        return NonRetriableBehavior.Fail

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        for backoff_strategy in self._backoff_strategies:
            backoff = backoff_strategy.backoff(response)
            if backoff:
                return backoff
        # None defaults to exponential backoff...
        return None
