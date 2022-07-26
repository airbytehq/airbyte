#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Final, List

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.types import Config

FALSE_VALUES: Final[List[Any]] = ["False", "false", "{}", "[]", "()", "", "0", "0.0", "False", "false", {}, False, [], (), set()]


class InterpolatedBoolean:
    f"""
    Wrapper around a string to be evaluated to a boolean value.
    The string will be evaluated as False if it interpolates to a value in {FALSE_VALUES}
    """

    def __init__(self, condition: str):
        """
        :param condition: The string representing the condition to evaluate to a boolean
        """
        self._condition = condition
        self._default = "False"
        self._interpolation = JinjaInterpolation()

    def eval(self, config: Config, **kwargs):
        """
        Interpolates the predicate condition string using the config and other optional arguments passed as parameter.

        :param config: The user-provided configuration as specified by the source's spec
        :param kwargs: Optional parameters used for interpolation
        :return: The interpolated string
        """
        if isinstance(self._condition, bool):
            return self._condition
        else:
            evaluated = self._interpolation.eval(self._condition, config, self._default, **kwargs)
            if evaluated in FALSE_VALUES:
                return False
            # The presence of a value is generally regarded as truthy, so we treat it as such
            return True
