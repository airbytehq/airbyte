from copy import deepcopy
from typing import Dict, TypeVar

from .frozen_error import FrozenError

__all__ = ["FrozenDict"]

KT = TypeVar("KT")
VT = TypeVar("VT", covariant=True)


class FrozenDict(Dict[KT, VT]):
    """Dictionary that can only be read, but not changed.

    .. deprecated:: 3.2
       Use dicts and the Mapping type instead. Will be removed in v3.3.
    """

    def __delitem__(self, key):
        raise FrozenError

    def __setitem__(self, key, value):
        raise FrozenError

    def __iadd__(self, value):
        raise FrozenError

    def __hash__(self):
        return hash(tuple(self.items()))

    def __copy__(self) -> "FrozenDict":
        return FrozenDict(self)

    copy = __copy__

    def __deepcopy__(self, memo: Dict) -> "FrozenDict":
        return FrozenDict({k: deepcopy(v, memo) for k, v in self.items()})

    def clear(self):
        raise FrozenError

    def pop(self, key, default=None):
        raise FrozenError

    def popitem(self):
        raise FrozenError

    def setdefault(self, key, default=None):
        raise FrozenError

    def update(self, other=None):
        raise FrozenError
