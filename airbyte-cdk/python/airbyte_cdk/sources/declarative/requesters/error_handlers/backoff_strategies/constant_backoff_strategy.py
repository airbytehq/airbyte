#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Optional

import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class ConstantBackoffStrategy(BackoffStrategy, JsonSchemaMixin):
    """
    Backoff strategy with a constant backoff interval

    Attributes:
        backoff_time_in_seconds (float): time to backoff before retrying a retryable request.
    """

    backoff_time_in_seconds: float

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        return self.backoff_time_in_seconds
