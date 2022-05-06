#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod
from typing import Tuple


class ConnectionChecker(ABC):
    @abstractmethod
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        pass
