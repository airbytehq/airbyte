#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Mapping

from airbyte_cdk.sources.cac.interpolation.interpolation import Interpolation


class InterpolatedMapping:
    def __init__(self, mapping: Mapping[str, str], interpolation: Interpolation):
        self._mapping = mapping
        self._interpolation = interpolation

    def eval(self, vars, config, **kwargs):
        print(f"interpolate: {self._mapping}")
        interpolated_values = {
            self._interpolation.eval(name, vars, config, **kwargs): self._interpolation.eval(value, vars, config, **kwargs)
            for name, value in self._mapping.items()
        }
        print(f"result: {interpolated_values}")

        non_null_values = {k: v for k, v in interpolated_values.items() if v}
        return non_null_values
