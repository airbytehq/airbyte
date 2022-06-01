#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


class InterpolatedBoolean:
    def __init__(self, condition):
        self._condition = condition
        self._default = "False"
        self._interpolation = JinjaInterpolation()

    def eval(self, config, **kwargs):
        if isinstance(self._condition, bool):
            return self._condition
        else:
            evaluated = self._interpolation.eval(self._condition, config, self._default, **kwargs)
            if evaluated == "True" or evaluated == "False":
                return True if evaluated == "True" else False
            if evaluated == "[]" or evaluated == "{}":
                return False
            # The presence of a value is generally regarded as truthy, so we treat it as such
            return True
