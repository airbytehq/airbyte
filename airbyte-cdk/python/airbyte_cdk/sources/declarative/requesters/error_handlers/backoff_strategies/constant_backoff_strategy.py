#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Callable, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ConstantBackoffStrategy as ConstantBackoffStrategyModel
from airbyte_cdk.sources.declarative.parsers.component_constructor import ComponentConstructor
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy
from airbyte_cdk.sources.types import Config
from pydantic import BaseModel


@dataclass
class ConstantBackoffStrategy(BackoffStrategy, ComponentConstructor):
    """
    Backoff strategy with a constant backoff interval

    Attributes:
        backoff_time_in_seconds (float): time to backoff before retrying a retryable request.
    """

    backoff_time_in_seconds: Union[float, InterpolatedString, str]
    parameters: InitVar[Mapping[str, Any]]
    config: Config

    @classmethod
    def resolve_dependencies(
        cls,
        model: ConstantBackoffStrategyModel,
        config: Config,
        dependency_constructor: Callable[[BaseModel, Config], Any],
        additional_flags: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        return {
            "backoff_time_in_seconds": model.backoff_time_in_seconds,
            "config": config,
            "parameters": model.parameters or {},
        }

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        if not isinstance(self.backoff_time_in_seconds, InterpolatedString):
            self.backoff_time_in_seconds = str(self.backoff_time_in_seconds)
        if isinstance(self.backoff_time_in_seconds, float):
            self.backoff_time_in_seconds = InterpolatedString.create(str(self.backoff_time_in_seconds), parameters=parameters)
        else:
            self.backoff_time_in_seconds = InterpolatedString.create(self.backoff_time_in_seconds, parameters=parameters)

    def backoff_time(
        self,
        response_or_exception: Optional[Union[requests.Response, requests.RequestException]],
        attempt_count: int,
    ) -> Optional[float]:
        return self.backoff_time_in_seconds.eval(self.config)  # type: ignore # backoff_time_in_seconds is always cast to an interpolated string
