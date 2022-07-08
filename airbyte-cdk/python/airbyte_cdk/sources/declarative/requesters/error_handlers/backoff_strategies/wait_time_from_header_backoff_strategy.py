#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import numbers
from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy


class WaitTimeFromHeaderBackoffStrategy(BackoffStrategy):
    """
    Extract wait time from http header
    """

    def __init__(self, header: str):
        """
        :param header: header to read wait time from
        """
        self._header = header

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        header_value = response.headers.get(self._header, None)
        if header_value and ((isinstance(header_value, str) and header_value.isnumeric()) or isinstance(header_value, numbers.Number)):
            return float(header_value)
        else:
            return None
