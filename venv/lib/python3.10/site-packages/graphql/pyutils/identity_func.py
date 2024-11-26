from typing import cast, Any, TypeVar

from .undefined import Undefined

__all__ = ["identity_func"]


T = TypeVar("T")


def identity_func(x: T = cast(Any, Undefined), *_args: Any) -> T:
    """Return the first received argument."""
    return x
