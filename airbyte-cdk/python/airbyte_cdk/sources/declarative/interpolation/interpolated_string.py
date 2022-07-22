#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.types import Config


class InterpolatedString:
    """
    Wrapper around a raw string to be interpolated with the Jinja2 templating engine
    """

    def __init__(self, string: str, default: Optional[str] = None):
        """
        :param string: string to evalute
        :param default: Default value to return if the evaluation returns an empty string
        """
        self._string = string
        self._default = default or string
        self._interpolation = JinjaInterpolation()

    def eval(self, config: Config, **kwargs):
        """
        Interpolates the input string using the config, and kwargs passed as parameter.

        :param config: The user-provided configuration as specified by the source's spec
        :param kwargs: Optional parameters used for interpolation
        :return: The interpolated string
        """
        return self._interpolation.eval(self._string, config, self._default, **kwargs)

    def __eq__(self, other):
        if not isinstance(other, InterpolatedString):
            return False
        return self._string == other._string and self._default == other._default
