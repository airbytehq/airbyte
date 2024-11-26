"""Command line interface for the dagger extension runtime."""
import inspect
import logging
import sys
from importlib import import_module
from typing import cast

import rich.traceback
from rich.console import Console

from . import default_module
from ._exceptions import FatalError, UserError
from ._module import Module

errors = Console(stderr=True, style="red")
logger = logging.getLogger(__name__)


def app():
    """Entrypoint for a dagger extension."""
    # TODO: Create custom exception hook to control exit code.
    rich.traceback.install(
        console=errors,
        show_locals=logger.isEnabledFor(logging.DEBUG),
        suppress=[
            "asyncio",
            "anyio",
        ],
    )
    try:
        mod = get_module()
        mod()
    except FatalError as e:
        if logger.isEnabledFor(logging.DEBUG):
            logger.exception("Fatal error")
        e.rich_print()
        sys.exit(1)


def get_module(module_name: str = "main") -> Module:
    """Get the environment instance from the main module."""
    # TODO: Allow configuring which package/module to use.
    try:
        py_module = import_module(module_name)
    except ModuleNotFoundError as e:
        msg = (
            f'The "{module_name}" module could not be found. '
            f'Did you create a "src/{module_name}.py" file in the root of your project?'
        )
        raise UserError(msg) from e

    # Check for any attribute that is an instance of `Module`.
    mods = (
        cast(Module, attr)
        for name, attr in inspect.getmembers(
            py_module, lambda obj: isinstance(obj, Module)
        )
        if not name.startswith("_")
    )

    # Use the default module unless the user overrides it with own instance.
    if not (mod := next(mods, None)):
        return default_module()

    # We could pick the first but it can be confusing to ignore the others.
    if next(mods, None):
        cls_path = f"{Module.__module__}.{Module.__qualname__}"
        msg = (
            f"Multiple `{cls_path}` instances were found in module {module_name}."
            " Please ensure that there is only one defined."
        )
        raise UserError(msg)

    return mod
