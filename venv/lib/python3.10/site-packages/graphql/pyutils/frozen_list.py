from copy import deepcopy
from typing import Dict, List, TypeVar

from .frozen_error import FrozenError

__all__ = ["FrozenList"]


T = TypeVar("T", covariant=True)


class FrozenList(List[T]):
    """List that can only be read, but not changed.

    .. deprecated:: 3.2
       Use tuples or lists and the Collection type instead. Will be removed in v3.3.
    """

    def __delitem__(self, key):
        raise FrozenError

    def __setitem__(self, key, value):
        raise FrozenError

    def __add__(self, value):
        if isinstance(value, tuple):
            value = list(value)
        return list.__add__(self, value)

    def __iadd__(self, value):
        raise FrozenError

    def __mul__(self, value):
        return list.__mul__(self, value)

    def __imul__(self, value):
        raise FrozenError

    def __hash__(self):
        return hash(tuple(self))

    def __copy__(self) -> "FrozenList":
        return FrozenList(self)

    def __deepcopy__(self, memo: Dict) -> "FrozenList":
        return FrozenList(deepcopy(value, memo) for value in self)

    def append(self, x):
        raise FrozenError

    def extend(self, iterable):
        raise FrozenError

    def insert(self, i, x):
        raise FrozenError

    def remove(self, x):
        raise FrozenError

    def pop(self, i=None):
        raise FrozenError

    def clear(self):
        raise FrozenError

    def sort(self, *, key=None, reverse=False):
        raise FrozenError

    def reverse(self):
        raise FrozenError
