#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Union

import airbyte_cdk.sources.declarative.requesters.error_handlers.response_status as response_status
import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus


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
                - type: "ConstantBackoffStrategy"
                  backoff_time_in_seconds: 5
            - response_filters:
                - http_codes: [ 403 ]
                  action: RETRY
              backoff_strategies:
                - type: "ConstantBackoffStrategy"
                  backoff_time_in_seconds: 10
    """

    def __init__(self, error_handlers: List[ErrorHandler]):
        """
        :param error_handlers: list of error handlers
        """
        self._error_handlers = error_handlers
        if not self._error_handlers:
            raise ValueError("CompositeErrorHandler expects at least 1 underlying error handler")

    @property
    def max_retries(self) -> Union[int, None]:
        return self._error_handlers[0].max_retries

    def should_retry(self, response: requests.Response) -> ResponseStatus:
        should_retry = None
        for retrier in self._error_handlers:
            should_retry = retrier.should_retry(response)
            if should_retry.action == ResponseAction.SUCCESS:
                return response_status.SUCCESS
            if should_retry == response_status.IGNORE or should_retry.action == ResponseAction.RETRY:
                return should_retry
        return should_retry
