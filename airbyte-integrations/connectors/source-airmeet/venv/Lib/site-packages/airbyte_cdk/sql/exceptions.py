# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""All exceptions used in Airbyte.

This design is modeled after structlog's exceptions, in that we bias towards auto-generated
property prints rather than sentence-like string concatenation.

E.g. Instead of this:

> `Subprocess failed with exit code '1'`

We do this:

> `Subprocess failed. (exit_code=1)`

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

import logging
from dataclasses import dataclass
from pathlib import Path
from textwrap import indent
from typing import Any

NEW_ISSUE_URL = "https://github.com/airbytehq/airbyte/issues/new/choose"
DOCS_URL_BASE = "https://https://docs.airbyte.com/"
DOCS_URL = f"{DOCS_URL_BASE}/airbyte.html"

VERTICAL_SEPARATOR = "\n" + "-" * 60


# Base error class


@dataclass
class AirbyteError(Exception):
    """Base class for exceptions in Airbyte."""

    guidance: str | None = None
    help_url: str | None = None
    log_text: str | list[str] | None = None
    log_file: Path | None = None
    context: dict[str, Any] | None = None
    message: str | None = None
    original_exception: Exception | None = None

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
        """Return a string representation of the exception."""
        special_properties = [
            "message",
            "guidance",
            "help_url",
            "log_text",
            "context",
            "log_file",
            "original_exception",
        ]
        display_properties = {
            k: v
            for k, v in self.__dict__.items()
            if k not in special_properties and not k.startswith("_") and v is not None
        }
        display_properties.update(self.context or {})
        context_str = "\n    ".join(
            f"{str(k).replace('_', ' ').title()}: {v!r}" for k, v in display_properties.items()
        )
        exception_str = (
            f"{self.get_message()} ({self.__class__.__name__})"
            + VERTICAL_SEPARATOR
            + f"\n{self.__class__.__name__}: {self.get_message()}"
        )

        if self.guidance:
            exception_str += f"\n    {self.guidance}"

        if self.help_url:
            exception_str += f"\n    More info: {self.help_url}"

        if context_str:
            exception_str += "\n    " + context_str

        if self.log_file:
            exception_str += f"\n    Log file: {self.log_file.absolute()!s}"

        if self.log_text:
            if isinstance(self.log_text, list):
                self.log_text = "\n".join(self.log_text)

            exception_str += f"\n    Log output: \n    {indent(self.log_text, '    ')}"

        if self.original_exception:
            exception_str += VERTICAL_SEPARATOR + f"\nCaused by: {self.original_exception!s}"

        return exception_str

    def __repr__(self) -> str:
        """Return a string representation of the exception."""
        class_name = self.__class__.__name__
        properties_str = ", ".join(
            f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_")
        )
        return f"{class_name}({properties_str})"

    def safe_logging_dict(self) -> dict[str, Any]:
        """Return a dictionary of the exception's properties which is safe for logging.

        We avoid any properties which could potentially contain PII.
        """
        result = {
            # The class name is safe to log:
            "class": self.__class__.__name__,
            # We discourage interpolated strings in 'message' so that this should never contain PII:
            "message": self.get_message(),
        }
        safe_attrs = ["connector_name", "stream_name", "violation", "exit_code"]
        for attr in safe_attrs:
            if hasattr(self, attr):
                result[attr] = getattr(self, attr)

        return result


# Airbyte Internal Errors (these are probably bugs)


@dataclass
class AirbyteInternalError(AirbyteError):
    """An internal error occurred in Airbyte."""

    guidance = "Please consider reporting this error to the Airbyte team."
    help_url = NEW_ISSUE_URL


# Airbyte Input Errors (replaces ValueError for user input)


@dataclass
class AirbyteInputError(AirbyteError, ValueError):
    """The input provided to Airbyte did not match expected validation rules.

    This inherits from ValueError so that it can be used as a drop-in replacement for
    ValueError in the Airbyte API.
    """

    guidance = "Please check the provided value and try again."
    help_url = DOCS_URL
    input_value: str | None = None


# Normalization Errors


@dataclass
class AirbyteNameNormalizationError(AirbyteError, ValueError):
    """Error occurred while normalizing a table or column name."""

    guidance = (
        "Please consider renaming the source object if possible, or "
        "raise an issue in GitHub if not."
    )
    help_url = NEW_ISSUE_URL

    raw_name: str | None = None
    normalization_result: str | None = None


@dataclass
class AirbyteConnectorError(AirbyteError):
    """Error when running the connector."""

    connector_name: str | None = None

    def __post_init__(self) -> None:
        """Set the log file path for the connector."""
        self.log_file = self._get_log_file()
        if not self.guidance and self.log_file:
            self.guidance = "Please review the log file for more information."

    def _get_log_file(self) -> Path | None:
        """Return the log file path for the connector."""
        if self.connector_name:
            logger = logging.getLogger(f"airbyte.{self.connector_name}")

            log_paths: list[Path] = [
                Path(handler.baseFilename).absolute()
                for handler in logger.handlers
                if isinstance(handler, logging.FileHandler)
            ]

            if log_paths:
                return log_paths[0]

        return None


@dataclass
class AirbyteStreamNotFoundError(AirbyteConnectorError):
    """Connector stream not found."""

    stream_name: str | None = None
    available_streams: list[str] | None = None
