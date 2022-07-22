#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


class InterpolatedMapping:
    """Wrapper around a Mapping[str, str] to be evaluated to be evaluated."""

    def __init__(self, mapping: Mapping[str, Any], options: Mapping[str, Any]):
        """
        :param mapping: Mapping[str, str] to be evaluated
        :param options: Interpolation parameters propagated by parent component
        """
        self._mapping = mapping
        self._options = options
        self._interpolation = JinjaInterpolation()

    def eval(self, config, **kwargs):
        interpolated_values = {
            self._interpolation.eval(name, config, options=self._options, **kwargs): self._eval(value, config, **kwargs)
            for name, value in self._mapping.items()
        }
        return interpolated_values

    def _eval(self, value, config, **kwargs):
        # The values in self._mapping can be of Any type
        # We only want to interpolate them if they are strings
        if type(value) == str:
            return self._interpolation.eval(value, config, options=self._options, **kwargs)
        else:
            return value
