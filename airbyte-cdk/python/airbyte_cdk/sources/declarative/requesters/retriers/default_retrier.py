#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from typing import List, Optional, Union

import requests
from airbyte_cdk.sources.declarative.requesters.retriers.backoff_strategies.exponential_backoff_strategy import ExponentialBackoffStrategy
from airbyte_cdk.sources.declarative.requesters.retriers.backoff_strategy import BackoffStrategy
from airbyte_cdk.sources.declarative.requesters.retriers.http_response_filter import HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.retriers.retrier import (
    NonRetriableResponseStatus,
    ResponseStatus,
    Retrier,
    RetryResponseStatus,
)


class DefaultRetrier(Retrier):
    DEFAULT_BACKOFF_STRATEGY = ExponentialBackoffStrategy()

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
        self._ignore_response_filter = ignore_response_filter or HttpResponseFilter(set())
        if backoff_strategy:
            self._backoff_strategy = backoff_strategy + [DefaultRetrier.DEFAULT_BACKOFF_STRATEGY]
        else:
            self._backoff_strategy = [DefaultRetrier.DEFAULT_BACKOFF_STRATEGY]

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
