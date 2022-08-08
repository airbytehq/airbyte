#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, List, Mapping, MutableMapping, Optional, Union

import airbyte_cdk.sources.declarative.requesters.error_handlers.response_status as response_status
import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.http_response_filter import HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class DefaultErrorHandler(ErrorHandler, JsonSchemaMixin):
    """
    Default error handler.

    By default, the handler will only retry server errors (HTTP 5XX) and too many requests (HTTP 429) with exponential backoff.

    If the response is successful, then return SUCCESS
    Otherwise, iterate over the response_filters.
    If any of the filter match the response, then return the appropriate status.
    If the match is RETRY, then iterate sequentially over the backoff_strategies and return the first non-None backoff time.

    Sample configs:

    1. retry 10 times
    `
        error_handler:
          max_retries: 10
    `
    2. backoff for 5 seconds
    `
        error_handler:
          backoff_strategies:
            - type: "ConstantBackoffStrategy"
              backoff_time_in_seconds: 5
    `
    3. retry on HTTP 404
    `
        error_handler:
          response_filters:
            - http_codes: [ 404 ]
              action: RETRY
    `
    4. ignore HTTP 404
    `
      error_handler:
        - http_codes: [ 404 ]
          action: IGNORE
    `
    5. retry if error message contains `retrythisrequest!` substring
    `
        error_handler:
          response_filters:
            - error_message_contain: "retrythisrequest!"
              action: IGNORE
    `
    6. retry if 'code' is a field present in the response body
    `
        error_handler:
          response_filters:
            - predicate: "{{ 'code' in response }}"
              action: IGNORE
    `

    7. ignore 429 and retry on 404
    `
        error_handler:
        - http_codes: [ 429 ]
          action: IGNORE
        - http_codes: [ 404 ]
          action: RETRY
    `

    Attributes:
        response_filters (Optional[List[HttpResponseFilter]]): response filters to iterate on
        max_retries (Optional[int]): maximum retry attempts
        backoff_strategies (Optional[List[BackoffStrategy]]): list of backoff strategies to use to determine how long
        to wait before retrying
    """

    DEFAULT_BACKOFF_STRATEGY = ExponentialBackoffStrategy

    options: InitVar[Mapping[str, Any]]
    response_filters: Optional[List[HttpResponseFilter]] = None
    max_retries: Optional[int] = 5
    _max_retries: int = field(init=False, repr=False, default=5)
    backoff_strategies: Optional[List[BackoffStrategy]] = None

    def __post_init__(self, options: Mapping[str, Any]):
        self.response_filters = self.response_filters or []

        if not self.response_filters:
            self.response_filters.append(
                HttpResponseFilter(ResponseAction.RETRY, http_codes=HttpResponseFilter.DEFAULT_RETRIABLE_ERRORS, options={})
            )
            self.response_filters.append(HttpResponseFilter(ResponseAction.IGNORE, options={}))

        if not self.backoff_strategies:
            self.backoff_strategies = [DefaultErrorHandler.DEFAULT_BACKOFF_STRATEGY()]

        self._last_request_to_attempt_count: MutableMapping[requests.PreparedRequest, int] = {}

    @property
    def max_retries(self) -> Union[int, None]:
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value: Union[int, None]):
        # Covers the case where max_retries is not provided in the constructor, which causes the property object
        # to be set which we need to avoid doing
        if not isinstance(value, property):
            self._max_retries = value

    def should_retry(self, response: requests.Response) -> ResponseStatus:
        request = response.request

        if request not in self._last_request_to_attempt_count:
            self._last_request_to_attempt_count = {request: 1}
        else:
            self._last_request_to_attempt_count[request] += 1
        for response_filter in self.response_filters:
            filter_action = response_filter.matches(response)
            if filter_action is not None:
                if filter_action == ResponseAction.RETRY:
                    return ResponseStatus(ResponseAction.RETRY, self._backoff_time(response, self._last_request_to_attempt_count[request]))
                else:
                    return ResponseStatus(filter_action)
        if response.ok:
            return response_status.SUCCESS
        # Fail if the response matches no filters
        return response_status.FAIL

    def _backoff_time(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        backoff = None
        for backoff_strategies in self.backoff_strategies:
            backoff = backoff_strategies.backoff(response, attempt_count)
            if backoff:
                return backoff
        return backoff
