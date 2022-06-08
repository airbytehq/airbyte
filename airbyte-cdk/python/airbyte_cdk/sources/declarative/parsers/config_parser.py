#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Mapping


class ConfigParser(ABC):
    @abstractmethod
    def parse(self, config_str: str) -> Mapping[str, Any]:
        pass
