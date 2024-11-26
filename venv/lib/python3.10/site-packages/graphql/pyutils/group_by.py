from collections import defaultdict
from typing import Callable, Collection, Dict, List, TypeVar

__all__ = ["group_by"]

K = TypeVar("K")
T = TypeVar("T")


def group_by(items: Collection[T], key_fn: Callable[[T], K]) -> Dict[K, List[T]]:
    """Group an unsorted collection of items by a key derived via a function."""
    result: Dict[K, List[T]] = defaultdict(list)
    for item in items:
        key = key_fn(item)
        result[key].append(item)
    return result
