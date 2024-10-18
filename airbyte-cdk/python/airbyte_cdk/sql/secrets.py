# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Base classes and methods for working with secrets in Airbyte."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, cast

from pydantic_core import CoreSchema, core_schema

from airbyte_cdk.sql import exceptions as exc


if TYPE_CHECKING:
    from pathlib import Path

    from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, ValidationInfo
    from pydantic.json_schema import JsonSchemaValue


class SecretSourceEnum(str, Enum):
    """Enumeration of secret sources supported by Airbyte."""

    ENV = "env"
    DOTENV = "dotenv"
    GOOGLE_COLAB = "google_colab"
    GOOGLE_GSM = "google_gsm"  # Not enabled by default

    PROMPT = "prompt"


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
        return core_schema.with_info_after_validator_function(function=cls.validate, schema=handler(str), field_name=handler.field_name)

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


class SecretManager(ABC):
    """Abstract base class for secret managers.

    Secret managers are used to retrieve secrets from a secret store.

    By registering a secret manager, Airbyte can automatically locate and
    retrieve secrets from the secret store when needed. This allows you to
    securely store and access sensitive information such as API keys, passwords,
    and other credentials without hardcoding them in your code.

    To create a custom secret manager, subclass this class and implement the
    `get_secret` method. By default, the secret manager will be automatically
    registered as a global secret source, but will not replace any existing
    secret sources. To customize this behavior, override the `auto_register` and
    `replace_existing` attributes in your subclass as needed.

    Note: Registered secrets managers always have priority over the default
    secret sources such as environment variables, dotenv files, and Google Colab
    secrets. If multiple secret managers are registered, the last one registered
    will take priority.
    """

    replace_existing = False
    as_backup = False

    def __init__(self) -> None:
        """Instantiate the new secret manager."""
        if not hasattr(self, "name"):
            # Default to the class name if no name is provided
            self.name: str = self.__class__.__name__

    @abstractmethod
    def get_secret(self, secret_name: str) -> SecretString | None:
        """Get a named secret from the secret manager.

        This method should be implemented by subclasses to retrieve secrets from
        the secret store. If the secret is not found, the method should return `None`.
        """
        ...

    def __str__(self) -> str:
        """Return the name of the secret manager."""
        return self.name

    def __eq__(self, value: object) -> bool:
        """Check if the secret manager is equal to another secret manager."""
        if isinstance(value, SecretManager):
            return self.name == value.name

        if isinstance(value, str):
            return self.name == value

        if isinstance(value, SecretSourceEnum):
            return self.name == str(value)

        return super().__eq__(value)

    def __hash__(self) -> int:
        """Return a hash of the secret manager name.

        This allows the secret manager to be used in sets and dictionaries.
        """
        return hash(self.name)


class SecretHandle:
    """A handle for a secret in a secret manager.

    This class is used to store a reference to a secret in a secret manager.
    The secret is not retrieved until the `get_value()` or `parse_json()` methods are
    called.
    """

    def __init__(
        self,
        parent: SecretManager,
        secret_name: str,
    ) -> None:
        """Instantiate a new secret handle."""
        self.parent = parent
        self.secret_name = secret_name

    def get_value(self) -> SecretString:
        """Get the secret from the secret manager.

        Subclasses can optionally override this method to provide a more optimized code path.
        """
        return cast(SecretString, self.parent.get_secret(self.secret_name))

    def parse_json(self) -> Any:
        """Parse the secret as JSON.

        This method is a convenience method to parse the secret as JSON without
        needing to call `get_value()` first. If the secret is not a valid JSON
        string, a `AirbyteInputError` will be raised.
        """
        return self.get_value().parse_json()

    def write_to_file(
        self,
        file_path: Path,
        /,
        *,
        silent: bool = False,
    ) -> None:
        """Write the secret to a file.

        If `silent` is True, the method will not print any output to the console. Otherwise,
        the method will print a message to the console indicating the file path to which the secret
        is being written.

        This method is a convenience method that writes the secret to a file as text.
        """
        if not silent:
            print(f"Writing secret '{self.secret_name.split('/')[-1]}' to '{file_path.absolute()!s}'")

        file_path.write_text(
            str(self.get_value()),
            encoding="utf-8",
        )
