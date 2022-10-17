#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy


class ConstantBackoffStrategy(BackoffStrategy):
    """
    Backoff strategy with a constant backoff interval
    """

    def __init__(self, backoff_time_in_seconds: float):
        """
        :param backoff_time_in_seconds: time to backoff before retrying a retryable request
        """
        self._backoff_time_in_seconds = backoff_time_in_seconds

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        return self._backoff_time_in_seconds
