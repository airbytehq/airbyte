from typing import (
    Any,
    ByteString,
    Collection,
    Iterable,
    Mapping,
    Text,
    ValuesView,
)

__all__ = ["is_collection", "is_iterable"]

collection_types: Any = Collection
if not isinstance({}.values(), Collection):  # Python < 3.7.2
    collection_types = (Collection, ValuesView)
iterable_types: Any = Iterable
not_iterable_types: Any = (ByteString, Mapping, Text)


def is_collection(value: Any) -> bool:
    """Check if value is a collection, but not a string or a mapping."""
    return isinstance(value, collection_types) and not isinstance(
        value, not_iterable_types
    )


def is_iterable(value: Any) -> bool:
    """Check if value is an iterable, but not a string or a mapping."""
    return isinstance(value, iterable_types) and not isinstance(
        value, not_iterable_types
    )
