#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.types import Config

NestedMappingEntry = Union[
    dict[str, "NestedMapping"], list["NestedMapping"], str, int, float, bool, None
]
NestedMapping = Union[dict[str, NestedMappingEntry], str, dict[str, Any]]


@dataclass
class InterpolatedNestedMapping:
    """
    Wrapper around a nested dict which can contain lists and primitive values where both the keys and values are interpolated recursively.

    Attributes:
        mapping (NestedMapping): to be evaluated
    """

    mapping: NestedMapping
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Optional[Mapping[str, Any]]) -> None:
        self._interpolation = JinjaInterpolation()
        self._parameters = parameters

    def eval(self, config: Config, **additional_parameters: Any) -> Any:
        return self._eval(self.mapping, config, **additional_parameters)

    def _eval(
        self, value: Union[NestedMapping, NestedMappingEntry], config: Config, **kwargs: Any
    ) -> Any:
        # Recursively interpolate dictionaries and lists
        if isinstance(value, str):
            return self._interpolation.eval(value, config, parameters=self._parameters, **kwargs)
        elif isinstance(value, dict):
            interpolated_dict = {
                self._eval(k, config, **kwargs): self._eval(v, config, **kwargs)
                for k, v in value.items()
            }
            return {k: v for k, v in interpolated_dict.items() if v is not None}
        elif isinstance(value, list):
            return [self._eval(v, config, **kwargs) for v in value]
        else:
            return value
