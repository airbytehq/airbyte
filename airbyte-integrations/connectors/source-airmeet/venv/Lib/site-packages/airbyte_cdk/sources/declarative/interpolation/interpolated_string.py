#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.types import Config


@dataclass
class InterpolatedString:
    """
    Wrapper around a raw string to be interpolated with the Jinja2 templating engine

    Attributes:
        string (str): The string to evalute
        default (Optional[str]): The default value to return if the evaluation returns an empty string
        parameters (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
    """

    string: str
    parameters: InitVar[Mapping[str, Any]]
    default: Optional[str] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.default = self.default or self.string
        self._interpolation = JinjaInterpolation()
        self._parameters = parameters
        # indicates whether passed string is just a plain string, not Jinja template
        # This allows for optimization, but we do not know it yet at this stage
        self._is_plain_string = None

    def eval(self, config: Config, **kwargs: Any) -> Any:
        """
        Interpolates the input string using the config and other optional arguments passed as parameter.

        :param config: The user-provided configuration as specified by the source's spec
        :param kwargs: Optional parameters used for interpolation
        :return: The interpolated string
        """
        if self._is_plain_string:
            return self.string
        if self._is_plain_string is None:
            # Let's check whether output from evaluation is the same as input.
            # This indicates occurrence of a plain string, not a template and we can skip Jinja in subsequent runs.
            evaluated = self._interpolation.eval(
                self.string, config, self.default, parameters=self._parameters, **kwargs
            )
            self._is_plain_string = self.string == evaluated
            return evaluated
        return self._interpolation.eval(
            self.string, config, self.default, parameters=self._parameters, **kwargs
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, InterpolatedString):
            return False
        return self.string == other.string and self.default == other.default

    @classmethod
    def create(
        cls,
        string_or_interpolated: Union["InterpolatedString", str],
        *,
        parameters: Mapping[str, Any],
    ) -> "InterpolatedString":
        """
        Helper function to obtain an InterpolatedString from either a raw string or an InterpolatedString.

        :param string_or_interpolated: either a raw string or an InterpolatedString.
        :param parameters: parameters propagated from parent component
        :return: InterpolatedString representing the input string.
        """
        if isinstance(string_or_interpolated, str):
            return InterpolatedString(string=string_or_interpolated, parameters=parameters)
        else:
            return string_or_interpolated
