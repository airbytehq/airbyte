# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Base classes and methods for working with secrets in Airbyte."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pydantic_core import CoreSchema, core_schema

from airbyte_cdk.sql import exceptions as exc

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, ValidationInfo
    from pydantic.json_schema import JsonSchemaValue


class SecretString(str):
    """A string that represents a secret.

    This class is used to mark a string as a secret. When a secret is printed, it
    will be masked to prevent accidental exposure of sensitive information when debugging
    or when printing containing objects like dictionaries.

    To create a secret string, simply instantiate the class with any string value:

        ```python
        secret = SecretString("my_secret_password")
        ```

    """

    __slots__ = ()

    def __repr__(self) -> str:
        """Override the representation of the secret string to return a masked value.

        The secret string is always masked with `****` to prevent accidental exposure, unless
        explicitly converted to a string. For instance, printing a config dictionary that contains
        a secret will automatically mask the secret value instead of printing it in plain text.

        However, if you explicitly convert the cast the secret as a string, such as when used
        in an f-string, the secret will be exposed. This is the desired behavior to allow
        secrets to be used in a controlled manner.
        """
        return "<SecretString: ****>"

    def is_empty(self) -> bool:
        """Check if the secret is an empty string."""
        return len(self) == 0

    def is_json(self) -> bool:
        """Check if the secret string is a valid JSON string."""
        try:
            json.loads(self)
        except (json.JSONDecodeError, Exception):
            return False

        return True

    def __bool__(self) -> bool:
        """Override the boolean value of the secret string.

        Always returns `True` without inspecting contents.
        """
        return True

    def parse_json(self) -> Any:
        """Parse the secret string as JSON."""
        try:
            return json.loads(self)
        except json.JSONDecodeError as ex:
            raise exc.AirbyteInputError(
                message="Failed to parse secret as JSON.",
                context={
                    "Message": ex.msg,
                    "Position": ex.pos,
                    "SecretString_Length": len(self),  # Debug secret blank or an unexpected format.
                },
            ) from None

    # Pydantic compatibility

    @classmethod
    def validate(
        cls,
        v: Any,  # noqa: ANN401  # Must allow `Any` to match Pydantic signature
        info: ValidationInfo,
    ) -> SecretString:
        """Validate the input value is valid as a secret string."""
        _ = info  # Unused
        if not isinstance(v, str):
            raise exc.AirbyteInputError(
                message="A valid `str` or `SecretString` object is required.",
            )
        return cls(v)

    @classmethod
    def __get_pydantic_core_schema__(  # noqa: PLW3201  # Pydantic dunder
        cls,
        source_type: Any,  # noqa: ANN401  # Must allow `Any` to match Pydantic signature
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Return a modified core schema for the secret string."""
        return core_schema.with_info_after_validator_function(
            function=cls.validate, schema=handler(str), field_name=handler.field_name
        )

    @classmethod
    def __get_pydantic_json_schema__(  # noqa: PLW3201  # Pydantic dunder method
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return a modified JSON schema for the secret string.

        - `writeOnly=True` is the official way to prevent secrets from being exposed inadvertently.
        - `Format=password` is a popular and readable convention to indicate the field is sensitive.
        """
        _ = _core_schema, handler  # Unused
        return {
            "type": "string",
            "format": "password",
            "writeOnly": True,
        }
