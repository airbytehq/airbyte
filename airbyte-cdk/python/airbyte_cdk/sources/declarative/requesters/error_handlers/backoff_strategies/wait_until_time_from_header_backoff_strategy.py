#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import numbers
import re
import time
from dataclasses import dataclass
from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.header_helper import get_numeric_value_from_header
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class WaitUntilTimeFromHeaderBackoffStrategy(BackoffStrategy, JsonSchemaMixin):
    """
    Extract time at which we can retry the request from response header
    and wait for the difference between now and that time

    Attributes:
        header (str): header to read wait time from
        min_wait (Optional[float]): minimum time to wait for safety
        regex (Optional[str]): optional regex to apply on the header to extract its value
    """

    header: str
    min_wait: Optional[float] = None
    regex: Optional[str] = None

    def __post_init__(self):
        self.regex = re.compile(self.regex) if self.regex else None

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        now = time.time()
        wait_until = get_numeric_value_from_header(response, self.header, self.regex)
        if wait_until is None or not wait_until:
            return self.min_wait
        if (isinstance(wait_until, str) and wait_until.isnumeric()) or isinstance(wait_until, numbers.Number):
            wait_time = float(wait_until) - now
        else:
            return self.min_wait
        if self.min_wait:
            return max(wait_time, self.min_wait)
        elif wait_time < 0:
            return None
        return wait_time
