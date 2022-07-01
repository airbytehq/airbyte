#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import time
from typing import List, Optional, Union

import requests
from airbyte_cdk.sources.declarative.requesters.retriers.backoff_strategy import BackoffStrategy
from airbyte_cdk.sources.declarative.requesters.retriers.http_response_filter import HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.retriers.retrier import (
    NonRetriableResponseStatus,
    ResponseStatus,
    Retrier,
    RetryResponseStatus,
)


class ExponentialBackoffStrategy(BackoffStrategy):
    def backoff(self, response: requests.Response) -> Optional[float]:
        return None


class StaticConstantBackoffStrategy(BackoffStrategy):
    def __init__(self, backoff_time_in_seconds: float):
        self._backoff_time_in_seconds = backoff_time_in_seconds

    def backoff(self, response: requests.Response) -> Optional[float]:
        return self._backoff_time_in_seconds


class WaitTimeFromHeaderBackoffStrategy(BackoffStrategy):
    def __init__(self, header: str):
        self._header = header

    def backoff(self, response: requests.Response) -> Optional[float]:
        return response.headers.get(self._header, None)


class WaitUntilTimeFromHeaderBackoffStrategy(BackoffStrategy):
    def __init__(self, header: str, min_wait: Optional[float] = None):
        self._header = header
        self._min_wait = min_wait

    def backoff(self, response: requests.Response) -> Optional[float]:
        now = time.time()
        wait_until = response.headers.get(self._header, None)
        if wait_until is None:
            return self._min_wait
        wait_time = float(wait_until) - now
        if self._min_wait:
            return max(wait_time, self._min_wait)
        elif wait_time < 0:
            return None
        return wait_time


class DefaultRetrier(Retrier):
    DEFAULT_BACKOFF_STRATEGSY = ExponentialBackoffStrategy()

    def __init__(
        self,
        retry_response_filter: HttpResponseFilter = None,
        ignore_response_filter: HttpResponseFilter = None,
        max_retries: Optional[int] = 5,
        retry_factor: float = 5,
        backoff_strategy: Optional[List[BackoffStrategy]] = None,
    ):
        self._max_retries = max_retries
        self._retry_factor = retry_factor
        self._retry_response_filter = retry_response_filter or HttpResponseFilter()
        self._ignore_response_filter = ignore_response_filter or HttpResponseFilter([])
        if backoff_strategy:
            self._backoff_strategy = backoff_strategy + [DefaultRetrier.DEFAULT_BACKOFF_STRATEGSY]
        else:
            self._backoff_strategy = [DefaultRetrier.DEFAULT_BACKOFF_STRATEGSY]

    @property
    def max_retries(self) -> Union[int, None]:
        return self._max_retries

    @property
    def retry_factor(self) -> float:
        return self._retry_factor

    def should_retry(self, response: requests.Response) -> ResponseStatus:
        if self._retry_response_filter.matches(response):
            return RetryResponseStatus(self._backoff_time(response))
        elif self._ignore_response_filter.matches(response):
            return NonRetriableResponseStatus.IGNORE
        elif response.ok:
            return NonRetriableResponseStatus.Ok
        else:
            return NonRetriableResponseStatus.FAIL

    def _backoff_time(self, response: requests.Response) -> Optional[float]:
        backoff = None
        for backoff_strategy in self._backoff_strategy:
            backoff = backoff_strategy.backoff(response)
            if backoff:
                return backoff
        return backoff
