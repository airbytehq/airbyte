#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Union

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import (
    ErrorHandler,
    NonRetriableResponseStatus,
    ResponseStatus,
    RetryResponseStatus,
)


class CompositeErrorHandler(ErrorHandler):
    """
    Sample config chaining 2 different retriers:
        retrier:
          type: "CompositeErrorHandler"
          retriers:
            - retry_response_filter:
                predicate: "{{ 'codase' in decoded_response }}"
              backoff_strategy:
                - type: "ConstantBackoffStrategy"
                  backoff_time_in_seconds: 5
            - retry_response_filter:
                http_codes: [ 403 ]
              backoff_strategy:
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
            if should_retry == NonRetriableResponseStatus.SUCCESS:
                return NonRetriableResponseStatus.SUCCESS
            if should_retry == NonRetriableResponseStatus.IGNORE:
                ignore = True
            elif not isinstance(retry, RetryResponseStatus):
                retry = should_retry
        if ignore:
            return NonRetriableResponseStatus.IGNORE
        else:
            return retry
