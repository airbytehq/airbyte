#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


class InterpolatedString:
    def __init__(self, string: str, default: Optional[str] = None):
        self._string = string
        self._default = default or string
        self._interpolation = JinjaInterpolation()

    def eval(self, config, **kwargs):
        return self._interpolation.eval(self._string, config, self._default, **kwargs)
