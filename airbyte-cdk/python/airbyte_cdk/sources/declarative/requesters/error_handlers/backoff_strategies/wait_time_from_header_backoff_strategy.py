#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import re
from dataclasses import dataclass
from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.header_helper import get_numeric_value_from_header
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class WaitTimeFromHeaderBackoffStrategy(BackoffStrategy, JsonSchemaMixin):
    """
    Extract wait time from http header

    Attributes:
        header (str): header to read wait time from
        regex (Optional[str]): optional regex to apply on the header to extract its value
    """

    header: str
    regex: Optional[str] = None

    def __post_init__(self):
        self.regex = re.compile(self.regex) if self.regex else None

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        header_value = get_numeric_value_from_header(response, self.header, self.regex)
        return header_value
