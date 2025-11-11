#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any


class ValidationStrategy(ABC):
    """
    Base class for validation strategies.
    """

    @abstractmethod
    def validate(self, value: Any) -> None:
        """
        Validates a value according to a specific strategy.

        :param value: The value to validate
        :raises ValueError: If validation fails
        """
        pass
