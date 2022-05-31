#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.interpolation.interpolation import Interpolation
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


class InterpolatedMapping:
    def __init__(self, mapping: Mapping[str, Any], interpolation: Interpolation = JinjaInterpolation()):
        self._mapping = mapping
        self._interpolation = interpolation

    def eval(self, config, **kwargs):
        interpolated_values = {
            self._interpolation.eval(name, config, **kwargs): self._eval(value, config, **kwargs) for name, value in self._mapping.items()
        }
        return interpolated_values

    def _eval(self, value, config, **kwargs):
        # The values in self._mapping can be of Any type
        # We only want to interpolate them if they are strings
        if type(value) == str:
            return self._interpolation.eval(value, config, **kwargs)
        else:
            return value
