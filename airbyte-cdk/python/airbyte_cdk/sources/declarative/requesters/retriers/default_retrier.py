#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional, Union

import requests
from airbyte_cdk.sources.declarative.requesters.retriers.backoff_strategies.exponential_backoff_strategy import ExponentialBackoffStrategy
from airbyte_cdk.sources.declarative.requesters.retriers.http_response_filter import HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.retriers.retrier import (
    NonRetriableResponseStatus,
    ResponseStatus,
    Retrier,
    RetryResponseStatus,
)
from pydantic import BaseModel


class DefaultRetrier(Retrier, BaseModel):
    """
    Sample configs:

    1. retry 10 times
    `
        retrier:
          max_retries: 10
    `
    2. backoff for 5 seconds
    `
        retrier:
          backoff_strategy:
            - type: "ConstantBackoffStrategy"
              backoff_time_in_seconds: 5
    `
    3. retry on HTTP 404
    `
        retrier:
          retry_response_filter:
            http_codes: [ 404 ]
    `
    4. ignore HTTP 404
    `
        retrier:
          ignore_response_filter:
            http_codes: [ 404 ]
    `
    5. retry if error message contains `retrythisrequest!` substring
    `
        retrier:
          retry_response_filter:
            error_message_contain: "retrythisrequest!"
    `
    6. retry if 'code' is a field present in the response body
    `
        retrier:
          retry_response_filter:
            predicate: "{{ 'code' in decoded_response }}"
    `
    """

    DEFAULT_BACKOFF_STRATEGY = ExponentialBackoffStrategy()

    retry_response_filter: Optional[HttpResponseFilter] = None
    ignore_response_filter: Optional[HttpResponseFilter] = None
    max_attempts: Optional[int] = 5
    exponential_retry_factor: float = 5
    # FIXME: missing some types here...
    backoff_strategy: Optional[List[Union[ExponentialBackoffStrategy]]] = None

    # def __init__(
    #        self,
    #        retry_response_filter: HttpResponseFilter = None,
    #        ignore_response_filter: HttpResponseFilter = None,
    #        max_retries: Optional[int] = 5,
    #        retry_factor: float = 5,
    #        backoff_strategy: Optional[List[BackoffStrategy]] = None,
    # ):
    # self._max_retries = max_retries
    # self._retry_factor = retry_factor
    # self._retry_response_filter = retry_response_filter or HttpResponseFilter()
    # self._ignore_response_filter = ignore_response_filter or HttpResponseFilter(set())

    # Always add the default backoff strategy as backup
    # if backoff_strategy:
    #    self._backoff_strategy = backoff_strategy + [DefaultRetrier.DEFAULT_BACKOFF_STRATEGY]
    # else:
    #    self._backoff_strategy = [DefaultRetrier.DEFAULT_BACKOFF_STRATEGY]

    @property
    def max_retries(self) -> Union[int, None]:
        return self.max_attempts

    @property
    def retry_factor(self) -> float:
        return self.exponential_retry_factor

    def should_retry(self, response: requests.Response) -> ResponseStatus:
        if self.retry_response_filter.matches(response):
            return RetryResponseStatus(self._backoff_time(response))
        elif self.ignore_response_filter.matches(response):
            return NonRetriableResponseStatus.IGNORE
        elif response.ok:
            return NonRetriableResponseStatus.Ok
        else:
            return NonRetriableResponseStatus.FAIL

    def _backoff_time(self, response: requests.Response) -> Optional[float]:
        backoff = None
        for backoff_strategy in self.backoff_strategy:
            backoff = backoff_strategy.backoff(response)
            if backoff:
                return backoff
        return backoff
