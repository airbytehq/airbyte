import inspect
from typing import Any
from types import CoroutineType, GeneratorType

__all__ = ["is_awaitable"]

CO_ITERABLE_COROUTINE = inspect.CO_ITERABLE_COROUTINE


def is_awaitable(value: Any) -> bool:
    """Return true if object can be passed to an ``await`` expression.

    Instead of testing if the object is an instance of abc.Awaitable, it checks
    the existence of an `__await__` attribute. This is much faster.
    """
    return (
        # check for coroutine objects
        isinstance(value, CoroutineType)
        # check for old-style generator based coroutine objects
        or isinstance(value, GeneratorType)
        and bool(value.gi_code.co_flags & CO_ITERABLE_COROUTINE)
        # check for other awaitables (e.g. futures)
        or hasattr(value, "__await__")
    )
