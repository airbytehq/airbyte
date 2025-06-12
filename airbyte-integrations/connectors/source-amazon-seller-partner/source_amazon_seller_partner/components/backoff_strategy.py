# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Optional, Union

import requests

from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.wait_time_from_header_backoff_strategy import (
    WaitTimeFromHeaderBackoffStrategy,
)


@dataclass
class AmazonSellerPartnerWaitTimeFromHeaderBackoffStrategy(WaitTimeFromHeaderBackoffStrategy):
    """
    This strategy is designed for scenarios where the server communicates retry-after durations
    through HTTP headers. The wait time is derived by taking the reciprocal of the value extracted
    from the header. If the header does not provide a valid time, a default backoff time is used.
    """

    default_backoff_time: Optional[float] = 10

    def backoff_time(
        self,
        response_or_exception: Optional[Union[requests.Response, requests.RequestException]],
        attempt_count: int,
    ) -> Optional[float]:
        time_from_header = super().backoff_time(response_or_exception, attempt_count)
        if time_from_header:
            return 1 / float(time_from_header)
        else:
            return self.default_backoff_time
