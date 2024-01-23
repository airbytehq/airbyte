"""All exceptions used in the Airbyte Lib.

This design is modeled after structlog's exceptions, in that we bias towards auto-generated
property prints rather than sentence-like string concatenation.

E.g. Instead of this:
> Subprocess failed with exit code '1'

We do this:
> Subprocess failed. (exit_code=1)

The benefit of this approach is that we can easily support structured logging, and we can
easily add new properties to exceptions without having to update all the places where they
are raised.

In addition, the following principles are applied for exception class design:
- All exceptions inherit from a common base class.
- All exceptions have a message attribute.
- The first line of the docstring is used as the default message.
- The default message can be overridden by explicitly setting the message attribute.
- Exceptions may optionally have a guidance attribute.
- Exceptions may optionally have a help_url attribute.
- Rendering is automatically handled by the base class.
- Exceptions are dataclasses, so they can be instantiated with keyword arguments.
"""
from __future__ import annotations

from abc import ABC
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class AirbyteError(Exception, ABC):
    """Base class for exceptions in Airbyte."""

    guidance: str | None = None
    help_url: str | None = None
    log_text: str | None = None
    more_context: dict[str, Any] | None = None

    @property
    def message(self) -> str:
        """By default we use the first line of the class's docstring as the message.

        Subclasses can override this property to provide a custom message.
        """
        return self.__doc__.split("\n")[0] if self.__doc__ else ""

    def __str__(self) -> str:
        special_properties = ["message", "guidance", "help_url", "log_text"]
        properties_str = ", ".join(
            f"{k}={v!r}"
            for k, v in asdict(self).items()
            if k not in special_properties and not k.startswith("_") and v is not None
        )
        exception_str = f"{self.message}."
        if properties_str:
            exception_str += f" ({properties_str})"
        if self.log_text:
            exception_str += f"\n\n Log output: {self.log_text}"
        if self.guidance:
            exception_str += f"\n\n Suggestion: {self.guidance}"
        if self.help_url:
            exception_str += f"\n\n More info: {self.help_url}"

        return exception_str

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        properties_str = ", ".join(
            f"{k}={v!r}" for k, v in asdict(self).items() if not k.startswith("_")
        )
        return f"{class_name}({properties_str})"


class AirbyteConnectorConfigurationMissingError(AirbyteError):
    """Connector is missing configuration."""

    connector_name: str


class AirbyteSubprocessError(AirbyteError):
    """Error when running subprocess."""

    args: list[str]


class AirbyteSubprocessFailedError(AirbyteSubprocessError):
    """Subprocess failed."""

    exit_code: int


class AirbyteConnectorRegistryError(AirbyteError):
    """Error when accessing the connector registry."""


class AirbyteConnectorNotFoundError(AirbyteError):
    """"Connector not found."""


class AirbyteConnectorInstallationError(AirbyteError):
    """Error when installing the connector."""


class AirbyteConnectorError(AirbyteError):
    """Exception raised for a specific error condition."""

    message = "Error when running the connector."


class AirbyteConnectorReadError(AirbyteError):
    """Error when reading from the connector."""


class AirbyteNoDataFromConnectorError(AirbyteError):
    """No data was provided from the connector."""


class AirbyteConnectorMissingCatalogError(AirbyteConnectorError):
    """Connector did not return a catalog."""


class AirbyteConnectorMissingSpecError(AirbyteConnectorError):
    """Connector did not return a spec."""


class AirbyteConnectorCheckFailedError(AirbyteConnectorError):
    """Connector did not return a spec."""


class AirbyteConnectorFailedError(AirbyteConnectorError):
    """Connector failed."""

    exit_code: int


class AirbyteStreamNotFoundError(AirbyteError):
    """Connector stream not found."""

    stream_name: str
    connector_name: str
    available_streams: list[str]
