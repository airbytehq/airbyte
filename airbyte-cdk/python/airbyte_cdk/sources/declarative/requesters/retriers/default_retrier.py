#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union

import requests
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.retriers.retrier import Retrier
from airbyte_cdk.sources.streams.http.http import HttpStream


class HttpResponseFilter:
    TOO_MANY_REQUESTS_ERRORS = [429]
    DEFAULT_RETRIABLE_ERRORS = [x for x in range(500, 600)] + TOO_MANY_REQUESTS_ERRORS

    def __init__(self, http_codes: List[int] = None, error_message_contain: str = None, predicate: str = ""):
        self._http_codes = http_codes or HttpResponseFilter.DEFAULT_RETRIABLE_ERRORS
        self._predicate = InterpolatedBoolean(predicate)
        self._error_message_contains = error_message_contain

    def matches(self, response: requests.Response) -> bool:
        return (
            response.status_code in self._http_codes
            or (self._response_matches_predicate(response))
            or (self._response_contains_error_message(response))
        )

    def _response_matches_predicate(self, response: requests.Response) -> bool:
        return self._predicate and self._predicate.eval(None, decoded_response=response.json())

    def _response_contains_error_message(self, response: requests.Response) -> bool:
        print(f"self._error_message_contains: {self._error_message_contains}")
        if not self._error_message_contains:
            return False
        else:
            return self._error_message_contains in HttpStream.parse_response_error_message(response)


class NonRetriableResponseStatus(Enum):
    Ok = ("OK",)
    FAIL = ("FAIL",)
    IGNORE = ("IGNORE",)


@dataclass
class RetryResponseStatus:
    retry_in: Optional[float]


ResponseStatus = Union[NonRetriableResponseStatus, RetryResponseStatus]


class BackoffStrategy:
    @abstractmethod
    def backoff(self, response: requests.Response) -> Optional[float]:
        pass


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


class ChainRetrier(Retrier):
    def __init__(self, retriers: List[Retrier]):
        self._retriers = retriers
        assert self._retriers

    @property
    def max_retries(self) -> Union[int, None]:
        # FIXME i think this should be moved to the backoff strategy!
        return self._iterate(Retrier.max_retries)

    @property
    def retry_factor(self) -> float:
        return self._iterate(Retrier.retry_factor)

    def should_retry(self, response: requests.Response) -> bool:
        retry = None
        ignore = False
        for retrier in self._retriers:
            should_retry = retrier.should_retry(response)
            if should_retry == NonRetriableResponseStatus.Ok:
                return NonRetriableResponseStatus.Ok
            if should_retry == NonRetriableResponseStatus.IGNORE:
                ignore = True
            elif not isinstance(retry, RetryResponseStatus):
                retry = should_retry
        if ignore:
            return NonRetriableResponseStatus.IGNORE
        else:
            return retry

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        pass

    def _iterate(self, f):
        val = None
        for retrier in self._retriers:
            val = f(retrier)
            if val:
                return val
        return val


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
            return RetryResponseStatus(self.backoff_time(response))
        elif self._ignore_response_filter.matches(response):
            return NonRetriableResponseStatus.IGNORE
        elif response.ok:
            return NonRetriableResponseStatus.Ok
        else:
            return NonRetriableResponseStatus.FAIL

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        for backoff_strategy in self._backoff_strategy:
            backoff = backoff_strategy.backoff(response)
            if backoff:
                return backoff
        return backoff
