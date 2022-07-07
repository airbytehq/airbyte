#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.retriers.backoff_strategy import BackoffStrategy


class ExponentialBackoffStrategy(BackoffStrategy):
    def __init__(self, max_attempts: int = 10, factor: float = 5):
        self._max_attempts = max_attempts
        self._factor = factor
        self._attempts_count = 0

    def backoff(self, response: requests.Response) -> Optional[float]:
        # Returning None backoff time makes the HttpStream use exponential backoff
        self._attempts_count += 1
        if self._attempts_count > self._max_attempts:
            return None
        else:
            return self._factor * 2**self._attempts_count
