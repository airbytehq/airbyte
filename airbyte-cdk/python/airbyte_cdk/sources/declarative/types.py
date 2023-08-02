#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Any, List, Mapping, Optional

# A FieldPointer designates a path to a field inside a mapping. For example, retrieving ["k1", "k1.2"] in the object {"k1" :{"k1.2":
# "hello"}] returns "hello"
FieldPointer = List[str]
Config = Mapping[str, Any]
ConnectionDefinition = Mapping[str, Any]
StreamSlice = Mapping[str, Any]
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
