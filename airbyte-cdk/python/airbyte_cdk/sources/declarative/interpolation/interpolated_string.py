#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Optional, Union

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


class InterpolatedString:
    def __init__(self, string: str, default: Optional[str] = None):
        self._string = string
        self._default = default or string
        self._interpolation = JinjaInterpolation()

    def eval(self, config, **kwargs):
        return self._interpolation.eval(self._string, config, self._default, **kwargs)

    def __eq__(self, other):
        if not isinstance(other, InterpolatedString):
            return False
        return self._string == other._string and self._default == other._default

    @classmethod
    def create(
        cls,
        string_or_interpolated: Union["InterpolatedString", str],
    ):
        """
        Helper function to obtain an InterpolatedString from either a raw string or an InterpolatedString.
        :param string_or_interpolated: either a raw string or an InterpolatedString.
        :param options: options parameters propagated from parent component
        :return: InterpolatedString representing the input string.
        """
        if isinstance(string_or_interpolated, str):
            return InterpolatedString(string_or_interpolated)
        else:
            return string_or_interpolated
