#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass
from typing import Any, List

import dpath.util

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.validators.validation_strategy import ValidationStrategy
from airbyte_cdk.sources.declarative.validators.validator import Validator

logger = logging.getLogger("airbyte")


@dataclass
class DpathValidator(Validator):
    """
    Validator that extracts a value at a specific path in the input data
    and applies a validation strategy to it.
    """

    field_path: List[str]
    strategy: ValidationStrategy

    def __post_init__(self) -> None:
        self._field_path = [
            InterpolatedString.create(path, parameters={}) for path in self.field_path
        ]
        for path_index in range(len(self.field_path)):
            if isinstance(self.field_path[path_index], str):
                self._field_path[path_index] = InterpolatedString.create(
                    self.field_path[path_index], parameters={}
                )

    def validate(self, input_data: dict[str, Any]) -> None:
        """
        Extracts the value at the specified path and applies the validation strategy.

        :param input_data: Dictionary containing the data to validate
        :raises ValueError: If the path doesn't exist or validation fails
        """
        path = [path.eval({}) for path in self._field_path]

        if len(path) == 0:
            raise ValueError("Field path is empty")

        if "*" in path:
            try:
                values = dpath.values(input_data, path)
                for value in values:
                    self.strategy.validate(value)
            except KeyError as e:
                logger.info(f"Validation skipped. Key not found: {e}")
                return

        else:
            try:
                value = dpath.get(input_data, path)
                self.strategy.validate(value)
            except KeyError as e:
                logger.info(f"Validation skipped. Key not found: {e}")
                return
