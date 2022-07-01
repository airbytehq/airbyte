#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import time
from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.retriers.backoff_strategy import BackoffStrategy


class WaitUntilTimeFromHeaderBackoffStrategy(BackoffStrategy):
    def __init__(self, header: str, min_wait: Optional[float] = None):
        self._header = header
        self._min_wait = min_wait

    def backoff(self, response: requests.Response) -> Optional[float]:
        now = time.time()
        wait_until = response.headers.get(self._header, None)
        if wait_until is None:
            return self._min_wait
        wait_time = float(wait_until) - now
        if self._min_wait:
            return max(wait_time, self._min_wait)
        elif wait_time < 0:
            return None
        return wait_time
