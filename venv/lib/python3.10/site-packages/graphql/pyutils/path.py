from typing import Any, List, NamedTuple, Optional, Union

__all__ = ["Path"]


class Path(NamedTuple):
    """A generic path of string or integer indices"""

    prev: Any  # Optional['Path'] (python/mypy/issues/731)
    """path with the previous indices"""
    key: Union[str, int]
    """current index in the path (string or integer)"""
    typename: Optional[str]
    """name of the parent type to avoid path ambiguity"""

    def add_key(self, key: Union[str, int], typename: Optional[str] = None) -> "Path":
        """Return a new Path containing the given key."""
        return Path(self, key, typename)

    def as_list(self) -> List[Union[str, int]]:
        """Return a list of the path keys."""
        flattened: List[Union[str, int]] = []
        append = flattened.append
        curr: Path = self
        while curr:
            append(curr.key)
            curr = curr.prev
        return flattened[::-1]
