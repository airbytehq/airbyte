#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any


class Validator(ABC):
    @abstractmethod
    def validate(self, input_data: Any) -> None:
        """
        Validates the input data.

        :param input_data: The data to validate
        :raises ValueError: If validation fails
        """
        pass
