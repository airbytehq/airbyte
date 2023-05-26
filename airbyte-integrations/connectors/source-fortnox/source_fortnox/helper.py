from collections.abc import Iterable
from typing import Any, Tuple


def signal_last(it: Iterable[Any]) -> Iterable[Tuple[bool, Any]]:
    """
    Helper method that wraps an iterator returns a tuple with the original
    element in the wrapped iterator as well as a boolean indicating
    if we are currently on the last iteration
    """
    try:
        iterable = iter(it)
        ret_var = next(iterable)
        for val in iterable:
            yield False, ret_var
            ret_var = val
        yield True, ret_var
    except StopIteration:
        yield from ()
