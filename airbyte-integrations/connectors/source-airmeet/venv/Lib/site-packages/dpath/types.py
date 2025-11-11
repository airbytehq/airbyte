from enum import IntFlag, auto
from typing import Union, Any, Callable, Sequence, Tuple, List, Optional, MutableMapping


class ListIndex(int):
    """Same as a normal int but mimics the behavior of list indices (can be compared to a negative number)."""

    def __new__(cls, value: int, list_length: int, *args, **kwargs):
        if value >= list_length:
            raise TypeError(
                f"Tried to initiate a {cls.__name__} with a value ({value}) "
                f"greater than the provided max value ({list_length})"
            )

        obj = super().__new__(cls, value)
        obj.list_length = list_length

        return obj

    def __eq__(self, other):
        if not isinstance(other, int):
            return False

        # Based on how Python sequences handle negative indices as described in footnote (3) of https://docs.python.org/3/library/stdtypes.html#common-sequence-operations
        return other == int(self) or self.list_length + other == int(self)

    def __repr__(self):
        return f"<{self.__class__.__name__} {int(self)}/{self.list_length}>"

    def __str__(self):
        return str(int(self))


class MergeType(IntFlag):
    ADDITIVE = auto()
    """List objects are combined onto one long list (NOT a set). This is the default flag."""

    REPLACE = auto()
    """Instead of combining list objects, when 2 list objects are at an equal depth of merge, replace the destination \
    with the source."""

    TYPESAFE = auto()
    """When 2 keys at equal levels are of different types, raise a TypeError exception. By default, the source \
    replaces the destination in this situation."""


PathSegment = Union[int, str, bytes]
"""Type alias for dict path segments where integers are explicitly casted."""

Filter = Callable[[Any], bool]
"""Type alias for filter functions.

(Any) -> bool"""

Glob = Union[str, Sequence[str]]
"""Type alias for glob parameters."""

Path = Union[str, Sequence[PathSegment]]
"""Type alias for path parameters."""

Hints = Sequence[Tuple[PathSegment, type]]
"""Type alias for creator function hint sequences."""

Creator = Callable[[Union[MutableMapping, List], Path, int, Optional[Hints]], None]
"""Type alias for creator functions.

Example creator function signature:

    def creator(
        current: Union[MutableMapping, List],
        segments: Sequence[PathSegment],
        i: int,
        hints: Sequence[Tuple[PathSegment, type]] = ()
    )"""
