#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import numbers
import time
from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy


class WaitUntilTimeFromHeaderBackoffStrategy(BackoffStrategy):
    """
    Extract time at which we can retry the request from response header
    and wait for the difference between now and that time
    """

    def __init__(self, header: str, min_wait: Optional[float] = None):
        """

        :param header: header to read wait time from
        :param min_wait: minimum time to wait for safety
        """
        self._header = header
        self._min_wait = min_wait

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        now = time.time()
        wait_until = response.headers.get(self._header, None)
        if wait_until is None or not wait_until:
            return self._min_wait
        if (isinstance(wait_until, str) and wait_until.isnumeric()) or isinstance(wait_until, numbers.Number):
            wait_time = float(wait_until) - now
        else:
            return self._min_wait
        if self._min_wait:
            return max(wait_time, self._min_wait)
        elif wait_time < 0:
            return None
        return wait_time
