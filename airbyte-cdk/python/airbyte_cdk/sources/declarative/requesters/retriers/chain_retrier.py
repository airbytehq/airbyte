#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Union

import requests
from airbyte_cdk.sources.declarative.requesters.retriers.retrier import (
    NonRetriableResponseStatus,
    ResponseStatus,
    Retrier,
    RetryResponseStatus,
)


class ChainRetrier(Retrier):
    """
    Sample config chaining 2 different retriers:
        retrier:
          type: "ChainRetrier"
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

    def __init__(self, retriers: List[Retrier]):
        self._retriers = retriers
        assert self._retriers

    @property
    def max_retries(self) -> Union[int, None]:
        return self._retriers[0].max_retries

    def should_retry(self, response: requests.Response) -> ResponseStatus:
        retry = None
        ignore = False
        for retrier in self._retriers:
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
