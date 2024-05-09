#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import numbers
import re
import time
from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.header_helper import get_numeric_value_from_header
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy
from airbyte_cdk.sources.types import Config


@dataclass
class WaitUntilTimeFromHeaderBackoffStrategy(BackoffStrategy):
    """
    Extract time at which we can retry the request from response header
    and wait for the difference between now and that time

    Attributes:
        header (str): header to read wait time from
        min_wait (Optional[float]): minimum time to wait for safety
        regex (Optional[str]): optional regex to apply on the header to extract its value
    """

    header: Union[InterpolatedString, str]
    parameters: InitVar[Mapping[str, Any]]
    config: Config
    min_wait: Optional[Union[float, InterpolatedString, str]] = None
    regex: Optional[Union[InterpolatedString, str]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.header = InterpolatedString.create(self.header, parameters=parameters)
        self.regex = InterpolatedString.create(self.regex, parameters=parameters) if self.regex else None
        if not isinstance(self.min_wait, InterpolatedString):
            self.min_wait = InterpolatedString.create(str(self.min_wait), parameters=parameters)

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        now = time.time()
        header = self.header.eval(self.config)  # type: ignore # header is always cast to an interpolated string
        if self.regex:
            evaled_regex = self.regex.eval(self.config)  # type: ignore # header is always cast to an interpolated string
            regex = re.compile(evaled_regex)
        else:
            regex = None
        wait_until = get_numeric_value_from_header(response, header, regex)
        min_wait = self.min_wait.eval(self.config)  # type: ignore # header is always cast to an interpolated string
        if wait_until is None or not wait_until:
            return float(min_wait) if min_wait else None
        if (isinstance(wait_until, str) and wait_until.isnumeric()) or isinstance(wait_until, numbers.Number):
            wait_time = float(wait_until) - now
        else:
            return float(min_wait)
        if min_wait:
            return float(max(wait_time, min_wait))
        elif wait_time < 0:
            return None
        return wait_time
