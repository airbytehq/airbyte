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
    def __init__(self, retriers: List[Retrier]):
        self._retriers = retriers
        assert self._retriers

    @property
    def max_retries(self) -> Union[int, None]:
        return self._iterate(Retrier.max_retries)

    @property
    def retry_factor(self) -> float:
        return self._iterate(Retrier.retry_factor)

    def should_retry(self, response: requests.Response) -> ResponseStatus:
        retry = None
        ignore = False
        for retrier in self._retriers:
            should_retry = retrier.should_retry(response)
            if should_retry == NonRetriableResponseStatus.Ok:
                return NonRetriableResponseStatus.Ok
            if should_retry == NonRetriableResponseStatus.IGNORE:
                ignore = True
            elif not isinstance(retry, RetryResponseStatus):
                retry = should_retry
        if ignore:
            return NonRetriableResponseStatus.IGNORE
        else:
            return retry

    def _iterate(self, f):
        val = None
        for retrier in self._retriers:
            val = retrier.f
            if val:
                return val
        return val
