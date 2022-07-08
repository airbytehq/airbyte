#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy


class ExponentialBackoffStrategy(BackoffStrategy):
    """
    Backoff strategy with an exponential backoff interval
    """

    def __init__(self, factor: float = 5):
        """
        :param factor: multiplicative factor
        """
        self._factor = factor

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        return self._factor * 2**attempt_count
