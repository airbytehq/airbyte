#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod

from airbyte_cdk.sources.declarative.types import Config


class Interpolation(ABC):
    @abstractmethod
    def eval(self, input_str: str, config: Config, **kwargs) -> str:
        pass
