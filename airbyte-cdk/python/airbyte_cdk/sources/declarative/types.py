#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Any, List, Mapping

# A FieldPointer designates a path to a field inside a mapping. For example, retrieving ["k1", "k1.2"] in the object {"k1" :{"k1.2":
# "hello"}] returns "hello"
FieldPointer = List[str]
Config = Mapping[str, Any]
ConnectionDefinition = Mapping[str, Any]
StreamSlice = Mapping[str, Any]
StreamState = Mapping[str, Any]


class Record(Mapping[str, Any]):
    def __init__(self, data: dict, associated_slice: StreamSlice):
        self._data = data
        self._associated_slice = associated_slice

    @property
    def data(self) -> dict:
        return self._data

    @property
    def associated_slice(self) -> StreamSlice:
        return self._associated_slice

    def __repr__(self):
        return repr(self._data)

    def __setitem__(self, key: str, value: Any):
        self._data[key] = value

    def __getitem__(self, key: str):
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __contains__(self, item: str):
        return item in self._data

    def __eq__(self, other):
        if isinstance(other, dict):
            return self._data == other
        if isinstance(other, Record):
            # noinspection PyProtectedMember
            return self._data == other._data
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
