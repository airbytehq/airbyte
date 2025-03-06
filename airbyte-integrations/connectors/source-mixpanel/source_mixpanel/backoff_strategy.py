#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta
from typing import Any, Optional, Union

import requests

from airbyte_cdk import BackoffStrategy
from airbyte_cdk.sources.streams.call_rate import APIBudget, HttpRequestMatcher, MovingWindowCallRatePolicy, Rate
from airbyte_cdk.sources.streams.http import HttpStream


DEFAULT_API_BUDGET = APIBudget(
    policies=[MovingWindowCallRatePolicy(rates=[Rate(limit=60, interval=timedelta(hours=1.0))], matchers=[HttpRequestMatcher()])]
)


class MixpanelStreamBackoffStrategy(BackoffStrategy):
    def __init__(self, stream: HttpStream, **kwargs):  # type: ignore # noqa
        self.stream = stream
        super().__init__(**kwargs)

    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        if isinstance(response_or_exception, requests.Response):
            retry_after = response_or_exception.headers.get("Retry-After")
            if retry_after:
                self._logger.debug(f"API responded with `Retry-After` header: {retry_after}")
                return float(retry_after)
        return None
