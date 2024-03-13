#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Any, ItemsView, Iterator, KeysView, List, Mapping, Optional, ValuesView

# A FieldPointer designates a path to a field inside a mapping. For example, retrieving ["k1", "k1.2"] in the object {"k1" :{"k1.2":
# "hello"}] returns "hello"
FieldPointer = List[str]
Config = Mapping[str, Any]
ConnectionDefinition = Mapping[str, Any]
StreamState = Mapping[str, Any]


class Record(Mapping[str, Any]):
    def __init__(self, data: Mapping[str, Any], associated_slice: Optional[StreamSlice]):
        self._data = data
        self._associated_slice = associated_slice

    @property
    def data(self) -> Mapping[str, Any]:
        return self._data

    @property
    def associated_slice(self) -> Optional[StreamSlice]:
        return self._associated_slice

    def __repr__(self) -> str:
        return repr(self._data)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Any:
        return iter(self._data)

    def __contains__(self, item: object) -> bool:
        return item in self._data

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Record):
            # noinspection PyProtectedMember
            return self._data == other._data
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class StreamSlice(Mapping[str, Any]):
    def __init__(self, *, partition: Mapping[str, Any], cursor_slice: Mapping[str, Any]) -> None:
        self._partition = partition
        self._cursor_slice = cursor_slice
        if partition.keys() & cursor_slice.keys():
            raise ValueError("Keys for partition and incremental sync cursor should not overlap")
        self._stream_slice = dict(partition) | dict(cursor_slice)

    @property
    def partition(self) -> Mapping[str, Any]:
        p = self._partition
        while isinstance(p, StreamSlice):
            p = p.partition
        return p

    @property
    def cursor_slice(self) -> Mapping[str, Any]:
        c = self._cursor_slice
        while isinstance(c, StreamSlice):
            c = c.cursor_slice
        return c

    def __repr__(self) -> str:
        return repr(self._stream_slice)

    def __setitem__(self, key: str, value: Any) -> None:
        raise ValueError("StreamSlice is immutable")

    def __getitem__(self, key: str) -> Any:
        return self._stream_slice[key]

    def __len__(self) -> int:
        return len(self._stream_slice)

    def __iter__(self) -> Iterator[str]:
        return iter(self._stream_slice)

    def __contains__(self, item: Any) -> bool:
        return item in self._stream_slice

    def keys(self) -> KeysView[str]:
        return self._stream_slice.keys()

    def items(self) -> ItemsView[str, Any]:
        return self._stream_slice.items()

    def values(self) -> ValuesView[Any]:
        return self._stream_slice.values()

    def get(self, key: str, default: Any = None) -> Optional[Any]:
        return self._stream_slice.get(key, default)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, dict):
            return self._stream_slice == other
        if isinstance(other, StreamSlice):
            # noinspection PyProtectedMember
            return self._partition == other._partition and self._cursor_slice == other._cursor_slice
        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
