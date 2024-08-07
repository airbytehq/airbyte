#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Final, List, Mapping

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.types import Config

FALSE_VALUES: Final[List[Any]] = ["False", "false", "{}", "[]", "()", "", "0", "0.0", {}, False, [], (), set()]


@dataclass
class InterpolatedBoolean:
    f"""
    Wrapper around a string to be evaluated to a boolean value.
    The string will be evaluated as False if it interpolates to a value in {FALSE_VALUES}

    Attributes:
        condition (str): The string representing the condition to evaluate to a boolean
    """
    condition: str
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._default = "False"
        self._interpolation = JinjaInterpolation()
        self._parameters = parameters

    def eval(self, config: Config, **additional_parameters: Any) -> bool:
        """
        Interpolates the predicate condition string using the config and other optional arguments passed as parameter.

        :param config: The user-provided configuration as specified by the source's spec
        :param additional_parameters: Optional parameters used for interpolation
        :return: The interpolated string
        """
        if isinstance(self.condition, bool):
            return self.condition
        else:
            evaluated = self._interpolation.eval(
                self.condition, config, self._default, parameters=self._parameters, **additional_parameters
            )
            if evaluated in FALSE_VALUES:
                return False
            # The presence of a value is generally regarded as truthy, so we treat it as such
            return True
