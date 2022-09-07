#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.types import Config
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class InterpolatedMapping(JsonSchemaMixin):
    """
    Wrapper around a Mapping[str, str] where both the keys and values are to be interpolated.

    Attributes:
        mapping (Mapping[str, str]): to be evaluated
    """

    mapping: Mapping[str, str]
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Optional[Mapping[str, Any]]):
        self._interpolation = JinjaInterpolation()
        self._options = options

    def eval(self, config: Config, **additional_options):
        """
        Wrapper around a Mapping[str, str] that allows for both keys and values to be interpolated.

        :param config: The user-provided configuration as specified by the source's spec
        :param additional_options: Optional parameters used for interpolation
        :return: The interpolated string
        """
        interpolated_values = {
            self._interpolation.eval(name, config, options=self._options, **additional_options): self._eval(
                value, config, **additional_options
            )
            for name, value in self.mapping.items()
        }
        return interpolated_values

    def _eval(self, value, config, **kwargs):
        # The values in self._mapping can be of Any type
        # We only want to interpolate them if they are strings
        if type(value) == str:
            return self._interpolation.eval(value, config, options=self._options, **kwargs)
        else:
            return value
