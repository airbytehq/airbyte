# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""All exceptions used in the PyAirbyte.

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
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from airbyte._util.api_duck_types import AirbyteApiResponseDuckType
    from airbyte.cloud.workspaces import CloudWorkspace


NEW_ISSUE_URL = "https://github.com/airbytehq/airbyte/issues/new/choose"
DOCS_URL_BASE = "https://airbytehq.github.io/PyAirbyte"
DOCS_URL = f"{DOCS_URL_BASE}/airbyte.html"

VERTICAL_SEPARATOR = "\n" + "-" * 60


# Base error class


@dataclass
class PyAirbyteError(Exception):
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


# PyAirbyte Internal Errors (these are probably bugs)


@dataclass
class PyAirbyteInternalError(PyAirbyteError):
    """An internal error occurred in PyAirbyte."""

    guidance = "Please consider reporting this error to the Airbyte team."
    help_url = NEW_ISSUE_URL


# PyAirbyte Input Errors (replaces ValueError for user input)


@dataclass
class PyAirbyteInputError(PyAirbyteError, ValueError):
    """The input provided to PyAirbyte did not match expected validation rules.

    This inherits from ValueError so that it can be used as a drop-in replacement for
    ValueError in the PyAirbyte API.
    """

    guidance = "Please check the provided value and try again."
    help_url = DOCS_URL
    input_value: str | None = None


@dataclass
class PyAirbyteNoStreamsSelectedError(PyAirbyteInputError):
    """No streams were selected for the source."""

    guidance = (
        "Please call `select_streams()` to select at least one stream from the list provided. "
        "You can also call `select_all_streams()` to select all available streams for this source."
    )
    connector_name: str | None = None
    available_streams: list[str] | None = None


# Normalization Errors


@dataclass
class PyAirbyteNameNormalizationError(PyAirbyteError, ValueError):
    """Error occurred while normalizing a table or column name."""

    guidance = (
        "Please consider renaming the source object if possible, or "
        "raise an issue in GitHub if not."
    )
    help_url = NEW_ISSUE_URL

    raw_name: str | None = None
    normalization_result: str | None = None


# PyAirbyte Cache Errors


class PyAirbyteCacheError(PyAirbyteError):
    """Error occurred while accessing the cache."""


@dataclass
class PyAirbyteCacheTableValidationError(PyAirbyteCacheError):
    """Cache table validation failed."""

    violation: str | None = None


@dataclass
class AirbyteConnectorConfigurationMissingError(PyAirbyteCacheError):
    """Connector is missing configuration."""

    connector_name: str | None = None


# Subprocess Errors


@dataclass
class AirbyteSubprocessError(PyAirbyteError):
    """Error when running subprocess."""

    run_args: list[str] | None = None


@dataclass
class AirbyteSubprocessFailedError(AirbyteSubprocessError):
    """Subprocess failed."""

    exit_code: int | None = None


# Connector Registry Errors


class AirbyteConnectorRegistryError(PyAirbyteError):
    """Error when accessing the connector registry."""


@dataclass
class AirbyteConnectorNotRegisteredError(AirbyteConnectorRegistryError):
    """Connector not found in registry."""

    connector_name: str | None = None
    guidance = (
        "Please double check the connector name. "
        "Alternatively, you can provide an explicit connector install method to `get_source()`: "
        "`pip_url`, `local_executable`, `docker_image`, or `source_manifest`."
    )
    help_url = DOCS_URL_BASE + "/airbyte/sources/util.html#get_source"


@dataclass
class AirbyteConnectorNotPyPiPublishedError(AirbyteConnectorRegistryError):
    """Connector found, but not published to PyPI."""

    connector_name: str | None = None
    guidance = "This likely means that the connector is not ready for use with PyAirbyte."


# Connector Errors


@dataclass
class AirbyteConnectorError(PyAirbyteError):
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


class AirbyteConnectorExecutableNotFoundError(AirbyteConnectorError):
    """Connector executable not found."""


class AirbyteConnectorInstallationError(AirbyteConnectorError):
    """Error when installing the connector."""


class AirbyteConnectorReadError(AirbyteConnectorError):
    """Error when reading from the connector."""


class AirbyteConnectorWriteError(AirbyteConnectorError):
    """Error when writing to the connector."""


class AirbyteConnectorSpecFailedError(AirbyteConnectorError):
    """Error when getting spec from the connector."""


class AirbyteConnectorDiscoverFailedError(AirbyteConnectorError):
    """Error when running discovery on the connector."""


class AirbyteNoDataFromConnectorError(AirbyteConnectorError):
    """No data was provided from the connector."""


class AirbyteConnectorMissingCatalogError(AirbyteConnectorError):
    """Connector did not return a catalog."""


class AirbyteConnectorMissingSpecError(AirbyteConnectorError):
    """Connector did not return a spec."""


class AirbyteConnectorValidationFailedError(AirbyteConnectorError):
    """Connector config validation failed."""

    guidance = (
        "Please double-check your config and review the validation errors for more information."
    )


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
class AirbyteStateNotFoundError(AirbyteConnectorError, KeyError):
    """State entry not found."""

    stream_name: str | None = None
    available_streams: list[str] | None = None


@dataclass
class PyAirbyteSecretNotFoundError(PyAirbyteError):
    """Secret not found."""

    guidance = "Please ensure that the secret is set."
    help_url = (
        "https://docs.airbyte.com/using-airbyte/airbyte-lib/getting-started#secrets-management"
    )

    secret_name: str | None = None
    sources: list[str] | None = None


# Airbyte API Errors


@dataclass
class AirbyteError(PyAirbyteError):
    """An error occurred while communicating with the hosted Airbyte instance."""

    response: AirbyteApiResponseDuckType | None = None
    """The API response from the failed request."""

    workspace: CloudWorkspace | None = None
    """The workspace where the error occurred."""

    @property
    def workspace_url(self) -> str | None:
        """The URL to the workspace where the error occurred."""
        if self.workspace:
            return self.workspace.workspace_url

        return None


@dataclass
class AirbyteConnectionError(AirbyteError):
    """An connection error occurred while communicating with the hosted Airbyte instance."""

    connection_id: str | None = None
    """The connection ID where the error occurred."""

    job_id: str | None = None
    """The job ID where the error occurred (if applicable)."""

    job_status: str | None = None
    """The latest status of the job where the error occurred (if applicable)."""

    @property
    def connection_url(self) -> str | None:
        """The URL to the connection where the error occurred."""
        if self.workspace_url and self.connection_id:
            return f"{self.workspace_url}/connections/{self.connection_id}"

        return None

    @property
    def job_history_url(self) -> str | None:
        """The URL to the job history where the error occurred."""
        if self.connection_url:
            return f"{self.connection_url}/job-history"

        return None

    @property
    def job_url(self) -> str | None:
        """The URL to the job where the error occurred."""
        if self.job_history_url and self.job_id:
            return f"{self.job_history_url}#{self.job_id}::0"

        return None


@dataclass
class AirbyteConnectionSyncError(AirbyteConnectionError):
    """An error occurred while executing the remote Airbyte job."""


@dataclass
class AirbyteConnectionSyncTimeoutError(AirbyteConnectionSyncError):
    """An timeout occurred while waiting for the remote Airbyte job to complete."""

    timeout: int | None = None
    """The timeout in seconds that was reached."""


# Airbyte Resource Errors (General)


@dataclass
class AirbyteMissingResourceError(AirbyteError):
    """Remote Airbyte resources does not exist."""

    resource_type: str | None = None
    resource_name_or_id: str | None = None


@dataclass
class AirbyteMultipleResourcesError(AirbyteError):
    """Could not locate the resource because multiple matching resources were found."""

    resource_type: str | None = None
    resource_name_or_id: str | None = None


# Custom Warnings


class AirbyteExperimentalFeatureWarning(FutureWarning):
    """Warning whenever using experimental features in PyAirbyte."""


# PyAirbyte Warnings


class PyAirbyteWarning(Warning):
    """General warnings from PyAirbyte."""


class PyAirbyteDataLossWarning(PyAirbyteWarning):
    """Warning for potential data loss.

    Users can ignore this warning by running:
    > warnings.filterwarnings("ignore", category="airbyte.exceptions.PyAirbyteDataLossWarning")
    """
