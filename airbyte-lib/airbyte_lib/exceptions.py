# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""All exceptions used in the Airbyte Lib.

This design is modeled after structlog's exceptions, in that we bias towards auto-generated
property prints rather than sentence-like string concatenation.

E.g. Instead of this:
> Subprocess failed with exit code '1'

We do this:
> Subprocess failed. (exit_code=1)

The benefit of this approach is that we can easily support structured logging, and we can
easily add new properties to exceptions without having to update all the places where they
are raised. We can also support any arbitrary number of properties in exceptions, without spending
time on building sentence-like string constructions with optional inputs.


In addition, the following principles are applied for exception class design:

- All exceptions inherit from a common base class.
- All exceptions have a message attribute.
- The first line of the docstring is used as the default message.
- The default message can be overridden by explicitly setting the message attribute.
- Exceptions may optionally have a guidance attribute.
- Exceptions may optionally have a help_url attribute.
- Rendering is automatically handled by the base class.
- Any helpful context not defined by the exception class can be passed in the `context` dict arg.
- Within reason, avoid sending PII to the exception constructor.
- Exceptions are dataclasses, so they can be instantiated with keyword arguments.
- Use the 'from' syntax to chain exceptions when it is helpful to do so.
  E.g. `raise AirbyteConnectorNotFoundError(...) from FileNotFoundError(connector_path)`
- Any exception that adds a new property should also be decorated as `@dataclass`.
"""
from __future__ import annotations

from dataclasses import dataclass
from textwrap import indent
from typing import Any


NEW_ISSUE_URL = "https://github.com/airbytehq/airbyte/issues/new/choose"
DOCS_URL = "https://docs.airbyte.io/"


# Base error class


@dataclass
class AirbyteError(Exception):
    """Base class for exceptions in Airbyte."""

    guidance: str | None = None
    help_url: str | None = None
    log_text: str | list[str] | None = None
    context: dict[str, Any] | None = None
    message: str | None = None

    def get_message(self) -> str:
        """Return the best description for the exception.

        We resolve the following in order:
        1. The message sent to the exception constructor (if provided).
        2. The first line of the class's docstring.
        """
        if self.message:
            return self.message

        return self.__doc__.split("\n")[0] if self.__doc__ else ""

    def __str__(self) -> str:
        special_properties = ["message", "guidance", "help_url", "log_text", "context"]
        display_properties = {
            k: v
            for k, v in self.__dict__.items()
            if k not in special_properties and not k.startswith("_") and v is not None
        }
        display_properties.update(self.context or {})
        context_str = "\n    ".join(
            f"{str(k).replace('_', ' ').title()}: {v!r}" for k, v in display_properties.items()
        )
        exception_str = f"{self.__class__.__name__}: {self.get_message()}\n"
        if context_str:
            exception_str += "    " + context_str

        if self.log_text:
            if isinstance(self.log_text, list):
                self.log_text = "\n".join(self.log_text)

            exception_str += f"\nLog output: \n    {indent(self.log_text, '    ')}"

        if self.guidance:
            exception_str += f"\nSuggestion: {self.guidance}"

        if self.help_url:
            exception_str += f"\nMore info: {self.help_url}"

        return exception_str

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        properties_str = ", ".join(
            f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_")
        )
        return f"{class_name}({properties_str})"


# AirbyteLib Internal Errors (these are probably bugs)


@dataclass
class AirbyteLibInternalError(AirbyteError):
    """An internal error occurred in Airbyte Lib."""

    guidance = "Please consider reporting this error to the Airbyte team."
    help_url = NEW_ISSUE_URL


# AirbyteLib Input Errors (replaces ValueError for user input)


@dataclass
class AirbyteLibInputError(AirbyteError, ValueError):
    """The input provided to AirbyteLib did not match expected validation rules.

    This inherits from ValueError so that it can be used as a drop-in replacement for
    ValueError in the Airbyte Lib API.
    """

    # TODO: Consider adding a help_url that links to the auto-generated API reference.

    guidance = "Please check the provided value and try again."
    input_value: str | None = None


@dataclass
class AirbyteLibNoStreamsSelectedError(AirbyteLibInputError):
    """No streams were selected for the source."""

    guidance = (
        "Please call `select_streams()` to select at least one stream from the list provided. "
        "You can also call `select_all_streams()` to select all available streams for this source."
    )
    connector_name: str | None = None
    available_streams: list[str] | None = None


# AirbyteLib Cache Errors


class AirbyteLibCacheError(AirbyteError):
    """Error occurred while accessing the cache."""


@dataclass
class AirbyteLibCacheTableValidationError(AirbyteLibCacheError):
    """Cache table validation failed."""

    violation: str | None = None


@dataclass
class AirbyteConnectorConfigurationMissingError(AirbyteLibCacheError):
    """Connector is missing configuration."""

    connector_name: str | None = None


# Subprocess Errors


@dataclass
class AirbyteSubprocessError(AirbyteError):
    """Error when running subprocess."""

    run_args: list[str] | None = None


@dataclass
class AirbyteSubprocessFailedError(AirbyteSubprocessError):
    """Subprocess failed."""

    exit_code: int | None = None


# Connector Registry Errors


class AirbyteConnectorRegistryError(AirbyteError):
    """Error when accessing the connector registry."""


@dataclass
class AirbyteConnectorNotRegisteredError(AirbyteConnectorRegistryError):
    """Connector not found in registry."""

    connector_name: str | None = None
    guidance = "Please double check the connector name."


@dataclass
class AirbyteConnectorNotPyPiPublishedError(AirbyteConnectorRegistryError):
    """Connector found, but not published to PyPI."""

    connector_name: str | None = None
    guidance = "This likely means that the connector is not ready for use with airbyte-lib."


# Connector Errors


@dataclass
class AirbyteConnectorError(AirbyteError):
    """Error when running the connector."""

    connector_name: str | None = None


class AirbyteConnectorExecutableNotFoundError(AirbyteConnectorError):
    """Connector executable not found."""


class AirbyteConnectorInstallationError(AirbyteConnectorError):
    """Error when installing the connector."""


class AirbyteConnectorReadError(AirbyteConnectorError):
    """Error when reading from the connector."""


class AirbyteNoDataFromConnectorError(AirbyteConnectorError):
    """No data was provided from the connector."""


class AirbyteConnectorMissingCatalogError(AirbyteConnectorError):
    """Connector did not return a catalog."""


class AirbyteConnectorMissingSpecError(AirbyteConnectorError):
    """Connector did not return a spec."""


class AirbyteConnectorCheckFailedError(AirbyteConnectorError):
    """Connector check failed."""

    guidance = (
        "Please double-check your config or review the connector's logs for more information."
    )


@dataclass
class AirbyteConnectorFailedError(AirbyteConnectorError):
    """Connector failed."""

    exit_code: int | None = None


@dataclass
class AirbyteStreamNotFoundError(AirbyteConnectorError):
    """Connector stream not found."""

    stream_name: str | None = None
    available_streams: list[str] | None = None


@dataclass
class AirbyteLibSecretNotFoundError(AirbyteError):
    """Secret not found."""

    guidance = "Please ensure that the secret is set."
    help_url = (
        "https://docs.airbyte.com/using-airbyte/airbyte-lib/getting-started#secrets-management"
    )

    secret_name: str | None = None
    sources: list[str] | None = None
