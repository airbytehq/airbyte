from collections.abc import Callable
from dataclasses import dataclass, field
from os import PathLike
from typing import Any, TextIO, TypeVar

import httpx
from rich.console import Console

__all__ = [
    "Config",
    "Retry",
    "Timeout",
]

_CallableT = TypeVar("_CallableT", bound=Callable[..., Any])
_Decorator = Callable[[_CallableT], _CallableT]


@dataclass(slots=True, kw_only=True)
class Retry:
    """Retry parameters for connecting to the Dagger API server."""

    connect: bool | _Decorator = True
    execute: bool | _Decorator = True


class Timeout(httpx.Timeout):
    @classmethod
    def default(cls) -> "Timeout":
        return cls(None, connect=10.0)


Timeout.__doc__ = httpx.Timeout.__doc__


@dataclass(slots=True, kw_only=True)
class ConnectConfig:
    timeout: Timeout | None = field(default_factory=Timeout.default)
    retry: Retry | None = field(default_factory=Retry)


UNSET = object()


@dataclass(slots=True, kw_only=True)
class Config(ConnectConfig):
    """Options for connecting to the Dagger engine.

    Parameters
    ----------
    workdir:
        The host workdir loaded into dagger.
    config_path:
        Project config file.
    log_output:
        A TextIO object to send the logs from the engine.
    timeout:
        The maximum time in seconds for establishing a connection to the server,
        or None to disable. Defaults to 10 seconds.
    execute_timeout:
        The maximum time in seconds for the execution of a request before an
        ExecuteTimeoutError is raised. Passing None results in waiting forever for a
        response (default).
    """

    workdir: PathLike[str] | str = ""
    config_path: PathLike[str] | str = ""
    log_output: TextIO | None = None
    execute_timeout: Any = UNSET
    console: Console = field(init=False)

    def __post_init__(self):
        # Backwards compability for (expected) use of `timeout` config.
        if self.timeout and not isinstance(self.timeout, Timeout):
            # TODO: deprecation warning: Use
            # self.timeout hasn't worked! (unused)
            timeout = self.timeout

            # used to be int
            try:
                timeout = float(timeout)
            except TypeError as e:
                msg = f"Wrong type for timeout: {type(timeout)}"
                raise TypeError(msg) from e

            self.timeout = Timeout(None, connect=timeout)

        # Backwards compability for `execute_timeout` config.
        if self.execute_timeout is not UNSET:
            # TODO: deprecation warning: Use `timeout` instead.
            timeout = self.execute_timeout

            # used to be int | float | None
            if timeout is not None:
                try:
                    timeout = float(timeout)
                except TypeError as e:
                    msg = f"Wrong type for execute_timeout: {type(timeout)}"
                    raise TypeError(msg) from e

            self.timeout = (
                Timeout(timeout, connect=self.timeout.connect)
                if self.timeout
                else Timeout(timeout)
            )

        self.console = Console(
            file=self.log_output,
            stderr=True,
        )
