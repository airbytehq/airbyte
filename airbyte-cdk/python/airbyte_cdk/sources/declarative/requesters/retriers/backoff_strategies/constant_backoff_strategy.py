#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.retriers.backoff_strategy import BackoffStrategy


class ConstantBackoffStrategy(BackoffStrategy):
    def __init__(self, backoff_time_in_seconds: float):
        self._backoff_time_in_seconds = backoff_time_in_seconds

    def backoff(self, response: requests.Response) -> Optional[float]:
        return self._backoff_time_in_seconds
