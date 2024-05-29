#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import DEFAULT_ERROR_RESOLUTION, ErrorResolution, ResponseAction


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

    def _new_error_resolution_is_preferred(
        self, new_error_resolution: Optional[ErrorResolution], current_error_resolution: Optional[ErrorResolution]
    ) -> bool:
        if new_error_resolution is None:
            return False

        if current_error_resolution is None:
            return True

        priority = {ResponseAction.FAIL: 0, ResponseAction.RETRY: 1, ResponseAction.IGNORE: 2, ResponseAction.SUCCESS: 3}

        return priority[new_error_resolution.response_action] > priority[current_error_resolution.response_action]

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        optimal_error_resolution = None
        for retrier in self.error_handlers:
            error_resolution = retrier.interpret_response(response_or_exception)
            if error_resolution is not None and self._new_error_resolution_is_preferred(
                new_error_resolution=error_resolution, current_error_resolution=optimal_error_resolution
            ):
                optimal_error_resolution = error_resolution

        if optimal_error_resolution is not None:
            return optimal_error_resolution
        return DEFAULT_ERROR_RESOLUTION
