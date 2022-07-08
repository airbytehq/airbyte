#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Union

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler, ResponseAction, ResponseStatus


class CompositeErrorHandler(ErrorHandler):
    """
    Sample config chaining 2 different retriers:
        error_handler:
          type: "CompositeErrorHandler"
          error_handlers:
            - response_filters:
                - predicate: "{{ 'codase' in decoded_response }}"
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
        self._error_handlers = error_handlers
        assert self._error_handlers

    @property
    def max_retries(self) -> Union[int, None]:
        return self._error_handlers[0].max_retries

    def should_retry(self, response: requests.Response) -> ResponseStatus:
        retry = None
        ignore = False
        for retrier in self._error_handlers:
            should_retry = retrier.should_retry(response)
            if should_retry.action == ResponseAction.SUCCESS:
                return ResponseStatus.success()
            if should_retry == ResponseStatus.ignore():
                ignore = True
            elif retry is None or retry.action != ResponseAction.RETRY:
                retry = should_retry
        if ignore:
            return ResponseStatus.ignore()
        else:
            return retry
