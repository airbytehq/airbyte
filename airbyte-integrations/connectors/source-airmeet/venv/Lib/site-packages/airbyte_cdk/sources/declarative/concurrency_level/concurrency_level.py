#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.types import Config


@dataclass
class ConcurrencyLevel:
    """
    Returns the number of worker threads that should be used when syncing concurrent streams in parallel

    Attributes:
        default_concurrency (Union[int, str]): The hardcoded integer or interpolation of how many worker threads to use during a sync
        max_concurrency (Optional[int]): The maximum number of worker threads to use when the default_concurrency is exceeded
    """

    default_concurrency: Union[int, str]
    max_concurrency: Optional[int]
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        if isinstance(self.default_concurrency, int):
            self._default_concurrency: Union[int, InterpolatedString] = self.default_concurrency
        elif "config" in self.default_concurrency and not self.max_concurrency:
            raise ValueError(
                "ConcurrencyLevel requires that max_concurrency be defined if the default_concurrency can be used-specified"
            )
        else:
            self._default_concurrency = InterpolatedString.create(
                self.default_concurrency, parameters=parameters
            )

    def get_concurrency_level(self) -> int:
        if isinstance(self._default_concurrency, InterpolatedString):
            evaluated_default_concurrency = self._default_concurrency.eval(config=self.config)
            if not isinstance(evaluated_default_concurrency, int):
                raise ValueError("default_concurrency did not evaluate to an integer")
            return (
                min(evaluated_default_concurrency, self.max_concurrency)
                if self.max_concurrency
                else evaluated_default_concurrency
            )
        else:
            return self._default_concurrency
