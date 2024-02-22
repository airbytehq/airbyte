# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Callable, Iterable, Mapping, Optional, Iterator, KeysView, ItemsView, ValuesView

from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


class PerPartitionStreamSlice(StreamSlice):
    def __init__(self, partition: Mapping[str, Any], cursor_slice: Mapping[str, Any]) -> None:
        self._partition = partition
        self._cursor_slice = cursor_slice
        if partition.keys() & cursor_slice.keys():
            raise ValueError("Keys for partition and incremental sync cursor should not overlap")
        self._stream_slice = dict(partition) | dict(cursor_slice)

    @property
    def partition(self) -> Mapping[str, Any]:
        return self._partition

    @property
    def cursor_slice(self) -> Mapping[str, Any]:
        return self._cursor_slice

    def __repr__(self) -> str:
        return repr(self._stream_slice)

    def __setitem__(self, key: str, value: Any) -> None:
        raise ValueError("PerPartitionStreamSlice is immutable")

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
        if isinstance(other, PerPartitionStreamSlice):
            # noinspection PyProtectedMember
            return self._partition == other._partition and self._cursor_slice == other._cursor_slice
        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
