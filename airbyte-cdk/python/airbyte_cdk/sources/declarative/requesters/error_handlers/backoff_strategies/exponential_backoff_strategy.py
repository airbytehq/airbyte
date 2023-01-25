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
class ExponentialBackoffStrategy(BackoffStrategy, JsonSchemaMixin):
    """
    Backoff strategy with an exponential backoff interval

    Attributes:
        factor (float): multiplicative factor
    """

    options: InitVar[Mapping[str, Any]]
    config: Config
    factor: Union[float, InterpolatedString, str] = 5

    def __post_init__(self, options: Mapping[str, Any]):
        if not isinstance(self.factor, InterpolatedString):
            self.factor = str(self.factor)
        self.factor = InterpolatedString.create(self.factor, options=options)

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        return self.factor.eval(self.config) * 2**attempt_count
