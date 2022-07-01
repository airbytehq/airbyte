#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.retriers.backoff_strategy import BackoffStrategy


class WaitTimeFromHeaderBackoffStrategy(BackoffStrategy):
    def __init__(self, header: str):
        self._header = header

    def backoff(self, response: requests.Response) -> Optional[float]:
        return response.headers.get(self._header, None)
