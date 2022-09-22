#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class ExponentialBackoffStrategy(BackoffStrategy, JsonSchemaMixin):
    """
    Backoff strategy with an exponential backoff interval

    Attributes:
        factor (float): multiplicative factor
    """

    factor: float = 5

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        return self.factor * 2**attempt_count
