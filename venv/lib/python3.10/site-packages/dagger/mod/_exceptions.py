from rich.console import Console
from rich.panel import Panel

from dagger import DaggerError

_console = Console(stderr=True, style="red")


class ExtensionError(DaggerError):
    """Base class for all errors raised by extensions."""

    def rich_print(self):
        _console.print(
            Panel(
                str(self),
                border_style="red",
                title="Error",
                title_align="left",
            )
        )


class FatalError(ExtensionError):
    """An unrecoverable error."""


class InternalError(FatalError):
    """An error in Dagger itself."""


class UserError(FatalError):
    """An error that could be recovered in user code."""


class NameConflictError(UserError):
    """An error caused by a name conflict."""


class FunctionError(UserError):
    """An error while executing a user function."""

    def __str__(self):
        return f"Function execution error: {super().__str__()}"
