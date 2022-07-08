#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import re
from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.header_helper import get_numeric_value_from_header
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy


class WaitTimeFromHeaderBackoffStrategy(BackoffStrategy):
    """
    Extract wait time from http header
    """

    def __init__(self, header: str, regex: Optional[str] = None):
        """
        :param header: header to read wait time from
        :param regex: optional regex to apply on the header to extract its value
        """
        self._header = header
        self._regex = re.compile(regex) if regex else None

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        header_value = get_numeric_value_from_header(response, self._header, self._regex)
        return header_value
