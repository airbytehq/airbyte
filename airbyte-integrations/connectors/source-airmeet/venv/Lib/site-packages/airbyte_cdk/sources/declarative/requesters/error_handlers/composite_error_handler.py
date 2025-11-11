#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Union

import requests

from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.backoff_strategy import BackoffStrategy
from airbyte_cdk.sources.streams.http.error_handlers.response_models import (
    ErrorResolution,
    ResponseAction,
    create_fallback_error_resolution,
)


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
    def max_retries(self) -> Optional[int]:
        return self.error_handlers[0].max_retries

    @property
    def max_time(self) -> Optional[int]:
        return max([error_handler.max_time or 0 for error_handler in self.error_handlers])

    def interpret_response(
        self, response_or_exception: Optional[Union[requests.Response, Exception]]
    ) -> ErrorResolution:
        matched_error_resolution = None
        for error_handler in self.error_handlers:
            matched_error_resolution = error_handler.interpret_response(response_or_exception)

            if not isinstance(matched_error_resolution, ErrorResolution):
                continue

            if matched_error_resolution.response_action in [
                ResponseAction.SUCCESS,
                ResponseAction.RETRY,
                ResponseAction.IGNORE,
                ResponseAction.RESET_PAGINATION,
            ]:
                return matched_error_resolution

        if matched_error_resolution:
            return matched_error_resolution

        return create_fallback_error_resolution(response_or_exception)

    @property
    def backoff_strategies(self) -> Optional[List[BackoffStrategy]]:
        """
        Combines backoff strategies from all child error handlers into a single flattened list.

        When used with HttpRequester, note the following behavior:
        - In HttpRequester.__post_init__, the entire list of backoff strategies is assigned to the error handler
        - However, the error handler's backoff_time() method only ever uses the first non-None strategy in the list
        - This means that if any backoff strategies are present, the first non-None strategy becomes the default
        - This applies to both user-defined response filters and errors from DEFAULT_ERROR_MAPPING
        - The list structure is not used to map different strategies to different error conditions
        - Therefore, subsequent strategies in the list will not be used

        Returns None if no handlers have strategies defined, which will result in HttpRequester using its default backoff strategy.
        """
        all_strategies = []
        for handler in self.error_handlers:
            if hasattr(handler, "backoff_strategies") and handler.backoff_strategies:
                all_strategies.extend(handler.backoff_strategies)
        return all_strategies if all_strategies else None
