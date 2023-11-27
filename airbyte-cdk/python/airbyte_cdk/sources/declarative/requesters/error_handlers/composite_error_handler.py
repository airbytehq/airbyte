#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Union

import airbyte_cdk.sources.declarative.requesters.error_handlers.response_status as response_status
import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus


@dataclass
class CompositeErrorHandler(ErrorHandler):
    """
    Error handler that sequentially iterates over a list of `ErrorHandler`s

    Sample config chaining 2 different retriers:
        error_handler:
          type: "CompositeErrorHandler"
          error_handlers:
            - response_filters:
                - predicate: "{{ 'codase' in response }}"
                  action: RETRY
              backoff_strategies:
                - type: "ConstantBackoff"
                  backoff_time_in_seconds: 5
            - response_filters:
                - http_codes: [ 403 ]
                  action: RETRY
              backoff_strategies:
                - type: "ConstantBackoff"
                  backoff_time_in_seconds: 10
    Attributes:
        error_handlers (List[ErrorHandler]): list of error handlers
    """

    error_handlers: List[ErrorHandler]
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        if not self.error_handlers:
            raise ValueError("CompositeErrorHandler expects at least 1 underlying error handler")

    @property
    def max_retries(self) -> Union[int, None]:
        return self.error_handlers[0].max_retries

    @property
    def max_time(self) -> Union[int, None]:
        return max([error_handler.max_time or 0 for error_handler in self.error_handlers])

    def interpret_response(self, response: requests.Response) -> ResponseStatus:
        should_retry = ResponseStatus(ResponseAction.FAIL)
        for retrier in self.error_handlers:
            should_retry = retrier.interpret_response(response)
            if should_retry.action == ResponseAction.SUCCESS:
                return response_status.SUCCESS
            if should_retry == response_status.IGNORE or should_retry.action == ResponseAction.RETRY:
                return should_retry
        return should_retry
