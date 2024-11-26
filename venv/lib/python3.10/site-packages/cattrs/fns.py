"""Useful internal functions."""
from typing import NoReturn, Type, TypeVar

from .errors import StructureHandlerNotFoundError

T = TypeVar("T")


def identity(obj: T) -> T:
    """The identity function."""
    return obj


def raise_error(_, cl: Type) -> NoReturn:
    """At the bottom of the condition stack, we explode if we can't handle it."""
    msg = f"Unsupported type: {cl!r}. Register a structure hook for it."
    raise StructureHandlerNotFoundError(msg, type_=cl)
