#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from dataclasses import dataclass
from typing import Any, Mapping

import jsonschema

from airbyte_cdk.sources.declarative.validators.validation_strategy import ValidationStrategy


@dataclass
class ValidateAdheresToSchema(ValidationStrategy):
    """
    Validates that a value adheres to a specified JSON schema.
    """

    schema: Mapping[str, Any]

    def validate(self, value: Any) -> None:
        """
        Validates the value against the JSON schema.

        :param value: The value to validate
        :raises ValueError: If the value does not adhere to the schema
        """

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string: {value}") from e

        try:
            jsonschema.validate(instance=value, schema=self.schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"JSON schema validation error: {e.message}")
