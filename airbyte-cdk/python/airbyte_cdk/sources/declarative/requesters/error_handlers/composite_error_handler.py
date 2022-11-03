#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Union

import airbyte_cdk.sources.declarative.requesters.error_handlers.response_status as response_status
import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class CompositeErrorHandler(ErrorHandler, JsonSchemaMixin):
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
                - type: "ConstantBackoffStrategy"
                  backoff_time_in_seconds: 5
            - response_filters:
                - http_codes: [ 403 ]
                  action: RETRY
              backoff_strategies:
                - type: "ConstantBackoffStrategy"
                  backoff_time_in_seconds: 10
    Attributes:
        error_handlers (List[ErrorHandler]): list of error handlers
    """

    error_handlers: List[ErrorHandler]
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        if not self.error_handlers:
            raise ValueError("CompositeErrorHandler expects at least 1 underlying error handler")

    @property
    def max_retries(self) -> Union[int, None]:
        return self.error_handlers[0].max_retries

    def should_retry(self, response: requests.Response) -> ResponseStatus:
        should_retry = None
        for retrier in self.error_handlers:
            should_retry = retrier.should_retry(response)
            if should_retry.action == ResponseAction.SUCCESS:
                return response_status.SUCCESS
            if should_retry == response_status.IGNORE or should_retry.action == ResponseAction.RETRY:
                return should_retry
        return should_retry
