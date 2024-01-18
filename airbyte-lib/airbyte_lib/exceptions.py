
class HostedAirbyteError(Exception):
    """Exception raised for failures working with hosted Airbyte."""

    def __init__(
        self,
        more_info: str | None = None,
        /,
    ) -> None:
        self.more_info = more_info

    @property
    def base_message(self) -> str:
        """Get the base message."""
        return "An error occurred while communicating with the hosted Airbyte instance."

    def __str__(self) -> str:
        """String representation of the error."""
        result = self.base_message

        if self.more_info:
            result += f" {self.more_info}"

        return result


class MissingResourceError(Exception):
    """Exception raised when a resource doesn't exist."""

    def __init__(
        self,
        name_or_id: str | None = None,
        /,
        resource_type: str | None = None,
        more_info: str | None = None,
    ) -> None:
        self.name_or_id = name_or_id
        self.resource_type = resource_type
        super().__init__(more_info)

    @property
    def base_message(self) -> str:
        """Get the base message."""
        result = f"Resource '{self.name_or_id}' does not exist"
        if self.resource_type:
            result += f" with type '{self.resource_type}'"

        result += "."
        return result


class HostedConnectionSyncError(Exception):
    """Exception raised when a hosted Airbyte connection fails to sync successfully."""

    def __init__(
        self,
        message: str | None = None,
        /,
        more_info: str | None = None,
    ) -> None:
        self.message = message
        super().__init__(more_info)

    @property
    def base_message(self) -> str:
        """Get the base message."""
        return f"An error occurred while executing an Airbyte job: {self.message}"
