#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Optional

from airbyte_cdk.sources.declarative.types import Config


class Interpolation(ABC):
    """
    Strategy for evaluating the interpolated value of a string at runtime using Jinja.
    """

    @abstractmethod
    def eval(self, input_str: str, config: Config, default: Optional[str] = None, **additional_options):
        """
        Interpolates the input string using the config, and additional options passed as parameter.

        :param input_str: The string to interpolate
        :param config: The user-provided configuration as specified by the source's spec
        :param default: Default value to return if the evaluation returns an empty string
        :param additional_options: Optional parameters used for interpolation
        :return: The interpolated string
        """
        pass
