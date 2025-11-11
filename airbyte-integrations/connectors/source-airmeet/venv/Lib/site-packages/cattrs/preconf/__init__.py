import sys
from datetime import datetime
from enum import Enum
from typing import Any, Callable, TypeVar, get_args

from .._compat import is_subclass
from ..converters import Converter, UnstructureHook
from ..fns import identity

if sys.version_info[:2] < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec


def validate_datetime(v, _):
    if not isinstance(v, datetime):
        raise Exception(f"Expected datetime, got {v}")
    return v


T = TypeVar("T")
P = ParamSpec("P")


def wrap(_: Callable[P, Any]) -> Callable[[Callable[..., T]], Callable[P, T]]:
    """Wrap a `Converter` `__init__` in a type-safe way."""

    def impl(x: Callable[..., T]) -> Callable[P, T]:
        return x

    return impl


def is_primitive_enum(type: Any, include_bare_enums: bool = False) -> bool:
    """Is this a string or int enum that can be passed through?"""
    return is_subclass(type, Enum) and (
        is_subclass(type, (str, int))
        or (include_bare_enums and type.mro()[1:] == Enum.mro())
    )


def literals_with_enums_unstructure_factory(
    typ: Any, converter: Converter
) -> UnstructureHook:
    """An unstructure hook factory for literals containing enums.

    If all contained enums can be passed through (their unstructure hook is `identity`),
    the entire literal can also be passed through.
    """
    if all(
        converter.get_unstructure_hook(type(arg)) == identity for arg in get_args(typ)
    ):
        return identity
    return converter.unstructure
