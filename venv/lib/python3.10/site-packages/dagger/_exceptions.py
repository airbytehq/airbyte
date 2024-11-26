from dataclasses import dataclass, field
from typing import Any

import cattrs
import graphql
from gql.transport.exceptions import TransportQueryError


class VersionMismatch(Warning):
    """Dagger CLI version doesn't match required version."""


class DaggerError(Exception):
    """Base exception for all Dagger exceptions."""


class ProvisionError(DaggerError):
    """Error while provisioning the Dagger engine."""


class DownloadError(ProvisionError):
    """Error while downloading the Dagger CLI."""

    def __str__(self) -> str:
        return f"Failed to download the Dagger CLI: {super().__str__()}"


class SessionError(ProvisionError):
    """Error while starting an engine session."""

    def __str__(self) -> str:
        return f"Failed to start Dagger engine session: {super().__str__()}"


class ClientError(DaggerError):
    """Base class for client errors."""


class ClientConnectionError(ClientError):
    """Error while establishing a client connection to the server."""

    def __str__(self) -> str:
        return (
            "Failed to establish client connection to the Dagger session: "
            f"{super().__str__()}"
        )


class TransportError(ClientError):
    """Error processing request/response during query execution."""


class ExecuteTimeoutError(TransportError):
    """Timeout while executing a query."""


class InvalidQueryError(ClientError):
    """Misuse of the query builder."""


@dataclass(slots=True)
class QueryErrorLocation:
    """Error location returned by the API."""

    line: int
    column: int


@dataclass(slots=True)
class QueryErrorValue:
    """An error value returned by the API."""

    message: str
    locations: list[QueryErrorLocation] | None = None
    path: list[str] | None = None
    extensions: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.message


class QueryError(ClientError):
    """The server returned an error for a specific query."""

    _type = None

    def __new__(cls, errors: list[QueryErrorValue], *_):
        error_types = {
            subclass._type: subclass  # noqa: SLF001
            for subclass in cls.__subclasses__()
            if subclass._type  # noqa: SLF001
        }
        try:
            new_type = error_types[errors[0].extensions["_type"]]
        except (KeyError, IndexError):
            return super().__new__(cls)
        return super().__new__(new_type)

    def __init__(self, errors: list[QueryErrorValue], query: graphql.DocumentNode):
        if not errors:
            msg = "Errors list is empty"
            raise ValueError(msg)
        super().__init__(errors[0])
        self.errors: list[QueryErrorValue] = errors
        self.query = query

    def debug_query(self):
        """Return GraphQL query for debugging purposes.

        Example::

            try:
                await ctr
            except dagger.QueryError as e:
                print(e.debug_query())
        """
        lines = graphql.print_ast(self.query).splitlines()
        # count number of digits from line count
        pad = len(str(len(lines)))
        locations = (
            {loc.line: loc.column for loc in self.errors[0].locations}
            if self.errors[0].locations
            else {}
        )
        res = []
        for nr, line in enumerate(lines, start=1):
            # prepend line number
            res.append(f"{{:{pad}d}}: {{}}".format(nr, line))
            if nr in locations:
                # add caret below line, pointing to start of error
                res.append(" " * (pad + 1 + locations[nr]) + "^")
        return "\n".join(res)


def _query_error_from_transport(exc: TransportQueryError, query: graphql.DocumentNode):
    """Create instance from a gql exception."""
    try:
        errors = cattrs.structure(exc.errors, list[QueryErrorValue])
    except (TypeError, KeyError, ValueError):
        return None
    return QueryError(errors, query) if errors else None


class ExecError(QueryError):
    """API error from an exec operation.

    Attributes
    ----------
    command:
        The command that was executed.
    message:
        The error message.
    exit_code:
        The exit code of the command.
    stdout:
        The stdout of the command.
    stderr:
        The stderr of the command.
    """

    _type = "EXEC_ERROR"

    command: list[str]
    message: str
    exit_code: int
    stdout: str
    stderr: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        error: QueryErrorValue = self.args[0]
        ext = error.extensions
        self.command = ext["cmd"]
        self.message = error.message
        self.exit_code = ext["exitCode"]
        self.stdout = ext["stdout"]
        self.stderr = ext["stderr"]

    def __str__(self):
        """Prints the error message with stdout and stderr."""
        # As a default when just printing the error, include the stdout
        # and stderr for visibility
        return f"{self.message}\nStdout:\n{self.stdout}\nStderr:\n{self.stderr}"


__all__ = [
    "VersionMismatch",
    "DaggerError",
    "ProvisionError",
    "DownloadError",
    "SessionError",
    "ClientError",
    "ClientConnectionError",
    "TransportError",
    "ExecuteTimeoutError",
    "InvalidQueryError",
    "QueryError",
    "ExecError",
]
