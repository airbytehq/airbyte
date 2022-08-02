#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy


@dataclass
class ExponentialBackoffStrategy(BackoffStrategy):
    """
    Backoff strategy with an exponential backoff interval
    """

    factor: float = 5

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        return self.factor * 2**attempt_count
