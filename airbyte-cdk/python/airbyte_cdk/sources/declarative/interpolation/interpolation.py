#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Optional

from airbyte_cdk.sources.declarative.types import Config


class Interpolation(ABC):
    """
    Strategy for evaluating the interpolated value of a string at runtime using Jinja.
    """

    @abstractmethod
    def eval(self, input_str: str, config: Config, default: Optional[str] = None, **kwargs):
        """
        Interpolates the input string using the config, and kwargs passed as paramter.

        :param input_str: The string to interpolate
        :param config: The user-provided configuration as specified by the source's spec
        :param default: Default value to return if the evaluation returns an empty string
        :param kwargs: Optional parameters used for interpolation
        :return: The interpolated string
        """
        pass
