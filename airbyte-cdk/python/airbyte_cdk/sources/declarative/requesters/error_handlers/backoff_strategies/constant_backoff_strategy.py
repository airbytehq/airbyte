#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy
from airbyte_cdk.sources.declarative.types import Config
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class ConstantBackoffStrategy(BackoffStrategy, JsonSchemaMixin):
    """
    Backoff strategy with a constant backoff interval

    Attributes:
        backoff_time_in_seconds (float): time to backoff before retrying a retryable request.
    """

    backoff_time_in_seconds: Union[float, InterpolatedString, str]
    options: InitVar[Mapping[str, Any]]
    config: Config

    def __post_init__(self, options: Mapping[str, Any]):
        if not isinstance(self.backoff_time_in_seconds, InterpolatedString):
            self.backoff_time_in_seconds = str(self.backoff_time_in_seconds)
        self.backoff_time_in_seconds = InterpolatedString.create(self.backoff_time_in_seconds, options=options)

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        return self.backoff_time_in_seconds.eval(self.config)
