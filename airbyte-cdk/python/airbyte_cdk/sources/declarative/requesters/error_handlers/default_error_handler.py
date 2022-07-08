#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, MutableMapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler, ResponseAction, ResponseStatus
from airbyte_cdk.sources.declarative.requesters.error_handlers.http_response_filter import HttpResponseFilter


class DefaultErrorHandler(ErrorHandler):
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

    DEFAULT_BACKOFF_STRATEGY = ExponentialBackoffStrategy

    def __init__(
        self,
        response_filters: Optional[List[HttpResponseFilter]] = None,
        max_retries: Optional[int] = 5,
        backoff_strategy: Optional[List[BackoffStrategy]] = None,
    ):
        self._max_retries = max_retries
        self._response_filters = response_filters or []

        if not self._has_retry_filter(self._response_filters):
            self._response_filters.append(HttpResponseFilter(ResponseAction.RETRY, http_codes=HttpResponseFilter.DEFAULT_RETRIABLE_ERRORS))
        if not self._has_ignore_filter(self._response_filters):
            self._response_filters.append(HttpResponseFilter(ResponseAction.IGNORE))

        if backoff_strategy:
            self._backoff_strategy = backoff_strategy
        else:
            self._backoff_strategy = [DefaultErrorHandler.DEFAULT_BACKOFF_STRATEGY()]

        self._last_request_to_attempt_count: MutableMapping[requests.PreparedRequest, int] = {}

    def _has_retry_filter(self, response_filters: List[HttpResponseFilter]):
        return self._has_filter_of_type(response_filters, ResponseAction)

    def _has_ignore_filter(self, response_filters: List[HttpResponseFilter]):
        return self._has_filter_of_type(response_filters, ResponseAction)

    def _has_filter_of_type(self, response_filters: List[HttpResponseFilter], filter_type: ResponseAction):
        if response_filters:
            return any([r.action == filter_type for r in response_filters])
        else:
            return False

    @property
    def max_retries(self) -> Union[int, None]:
        return self._max_retries

    def should_retry(self, response: requests.Response) -> ResponseStatus:
        request = response.request
        if response.ok:
            return ResponseStatus.success()
        if request not in self._last_request_to_attempt_count:
            self._last_request_to_attempt_count = {request: 1}
        else:
            self._last_request_to_attempt_count[request] += 1

        for response_filter in self._response_filters:
            filter_action = response_filter.matches(response)
            if filter_action is not None:
                if filter_action == ResponseAction.RETRY:
                    return ResponseStatus(ResponseAction.RETRY, self._backoff_time(response, self._last_request_to_attempt_count[request]))
                else:
                    return ResponseStatus(filter_action)
        # Fail if the response matches no filters
        return ResponseStatus.fail()

    def _backoff_time(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        backoff = None
        for backoff_strategies in self._backoff_strategy:
            backoff = backoff_strategies.backoff(response, attempt_count)
            if backoff:
                return backoff
        return backoff
