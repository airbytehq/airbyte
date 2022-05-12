#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.cac.interpolation.eval import JinjaInterpolation


class InterpolatedString:
    def __init__(self, string, default=None):
        self._string = string
        self._default = default or string
        self._interpolation = JinjaInterpolation()

    def eval(self, vars, config, **kwargs):
        return self._interpolation.eval(self._string, vars, config, self._default, **kwargs)
