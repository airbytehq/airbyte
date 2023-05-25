#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.types import Config

NestedMappingEntry = Union[dict[str, "NestedMapping"], list["NestedMapping"], str, int, float, bool, None]
NestedMapping = Union[dict[str, NestedMappingEntry], str]


@dataclass
class InterpolatedNestedMapping:
    """
    Wrapper around a nested dict which can contain lists and primitive values where both the keys and values are interpolated recursively.

    Attributes:
        mapping (NestedMapping): to be evaluated
    """

    mapping: NestedMapping
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Optional[Mapping[str, Any]]):
        self._interpolation = JinjaInterpolation()
        self._parameters = parameters

    def eval(self, config: Config, **additional_parameters):
        return self._eval(self.mapping, config, **additional_parameters)

    def _interpolate_dict(self, value, config, **kwargs):
        interpolated_dict = {}
        for k, v in value.items():
            interpolated_key = self._eval(k, config, **kwargs)
            interpolated_value = self._eval(v, config, **kwargs)
            if interpolated_value is not None:
                interpolated_dict[interpolated_key] = interpolated_value
        return interpolated_dict

    def _eval(self, value, config, **kwargs):
        # Recursively interpolate dictionaries and lists
        if isinstance(value, str):
            return self._interpolation.eval(value, config, parameters=self._parameters, **kwargs)
        elif isinstance(value, dict):
            return self._interpolate_dict(value, config, **kwargs)
        elif isinstance(value, list):
            return [self._eval(v, config, **kwargs) for v in value]
        else:
            return value
