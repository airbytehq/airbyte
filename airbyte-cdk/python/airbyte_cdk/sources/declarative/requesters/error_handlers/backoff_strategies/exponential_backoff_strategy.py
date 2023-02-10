#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class ExponentialBackoffStrategy(BackoffStrategy):
    """
    Backoff strategy with an exponential backoff interval

    Attributes:
        factor (float): multiplicative factor
    """

    parameters: InitVar[Mapping[str, Any]]
    config: Config
    factor: Union[float, InterpolatedString, str] = 5

    def __post_init__(self, parameters: Mapping[str, Any]):
        if not isinstance(self.factor, InterpolatedString):
            self.factor = str(self.factor)
        self.factor = InterpolatedString.create(self.factor, parameters=parameters)

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        return self.factor.eval(self.config) * 2**attempt_count
