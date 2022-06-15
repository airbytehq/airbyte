#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Optional, Union

import requests
from airbyte_cdk.sources.declarative.requesters.retriers.retrier import Retrier


class DefaultRetrier(Retrier):
    def __init__(self, max_retries: Optional[int] = 5, retry_factor: float = 5):
        self._max_retries = max_retries
        self._retry_factor = retry_factor

    @property
    def max_retries(self) -> Union[int, None]:
        return self._max_retries

    @property
    def retry_factor(self) -> float:
        return self._retry_factor

    def should_retry(self, response: requests.Response) -> bool:
        return response.status_code == 429 or 500 <= response.status_code < 600

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        return None
