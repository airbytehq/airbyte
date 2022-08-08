#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.types import Config
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class InterpolatedString(JsonSchemaMixin):
    """
    Wrapper around a raw string to be interpolated with the Jinja2 templating engine

    Attributes:
        string (str): The string to evalute
        default (Optional[str]): The default value to return if the evaluation returns an empty string
        options (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
    """

    string: str
    options: InitVar[Mapping[str, Any]]
    default: Optional[str] = None

    def __post_init__(self, options: Mapping[str, Any]):
        self.default = self.default or self.string
        self._interpolation = JinjaInterpolation()
        self._options = options

    def eval(self, config: Config, **kwargs):
        """
        Interpolates the input string using the config and other optional arguments passed as parameter.

        :param config: The user-provided configuration as specified by the source's spec
        :param kwargs: Optional parameters used for interpolation
        :return: The interpolated string
        """
        return self._interpolation.eval(self.string, config, self.default, options=self._options, **kwargs)

    def __eq__(self, other):
        if not isinstance(other, InterpolatedString):
            return False
        return self.string == other.string and self.default == other.default

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
            return InterpolatedString(string=string_or_interpolated, options=options)
        else:
            return string_or_interpolated
