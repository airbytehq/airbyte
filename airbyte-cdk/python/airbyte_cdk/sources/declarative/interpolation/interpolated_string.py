#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.types import Config


class InterpolatedString:
    """
    Wrapper around a raw string to be interpolated with the Jinja2 templating engine
    """

    def __init__(self, string: str, *, options: Mapping[str, Any] = {}, default: Optional[str] = None):
        """
        :param string: The string to evalute
        :param default: The default value to return if the evaluation returns an empty string
        :param options: Additional runtime parameters to be used for string interpolation
        """
        self._string = string
        self._default = default or string
        self._interpolation = JinjaInterpolation()
        self._options = options or {}

    def eval(self, config: Config, **kwargs):
        """
        Interpolates the input string using the config and other optional arguments passed as parameter.

        :param config: The user-provided configuration as specified by the source's spec
        :param kwargs: Optional parameters used for interpolation
        :return: The interpolated string
        """
        return self._interpolation.eval(self._string, config, self._default, options=self._options, **kwargs)

    def __eq__(self, other):
        if not isinstance(other, InterpolatedString):
            return False
        return self._string == other._string and self._default == other._default

    @classmethod
    def create(
        cls,
        string_or_interpolated: Union["InterpolatedString", str],
        *,
        options: Mapping[str, Any],
    ):
        """
        Helper function to obtain an InterpolatedString from either a raw string or an InterpolatedString.

        :param string_or_interpolated: either a raw string or an InterpolatedString.
        :param options: options parameters propagated from parent component
        :return: InterpolatedString representing the input string.
        """
        if isinstance(string_or_interpolated, str):
            return InterpolatedString(string_or_interpolated, options=options)
        else:
            return string_or_interpolated
