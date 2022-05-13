#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC, abstractmethod
from typing import Any, Mapping, Tuple


class ConnectionChecker(ABC):
    @abstractmethod
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        pass
