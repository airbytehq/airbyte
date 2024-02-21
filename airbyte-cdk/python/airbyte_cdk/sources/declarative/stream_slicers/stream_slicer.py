#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable

from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import RequestOptionsProvider
from airbyte_cdk.sources.declarative.types import StreamSlice


@dataclass
class StreamSlicer(RequestOptionsProvider):
    """
    Slices the stream into a subset of records.
    Slices enable state checkpointing and data retrieval parallelization.

    The stream slicer keeps track of the cursor state as a dict of cursor_field -> cursor_value

    See the stream slicing section of the docs for more information.
    """

    @abstractmethod
    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Defines stream slices

        :return: List of stream slices
        """


class DeclarativeStreamSlice(ABC):
    @property
    @abstractmethod
    def partition(self):
        """

        :return:
        """

    @property
    @abstractmethod
    def cursor_slice(self):
        """"""


class CursorSlice(DeclarativeStreamSlice):
    def __init__(self, slice_value):
        self._slice_value = slice_value

    @property
    def partition(self):
        return {}

    @property
    def cursor_slice(self):
        return self._slice_value

    def __repr__(self):
        return repr(self._slice_value)

    def __setitem__(self, key: str, value: Any):
        raise ValueError("CursorSlice is immutable")

    def __getitem__(self, key: str):
        return self._slice_value[key]

    def __len__(self):
        return len(self._slice_value)

    def __iter__(self):
        return iter(self._slice_value)

    def __contains__(self, item: str):
        return item in self._slice_value

    def keys(self):
        return self._slice_value.keys()

    def items(self):
        return self._slice_value.items()

    def values(self):
        return self._slice_value.values()

    def get(self, key: str, default: Any = None) -> Any:
        return self._slice_value.get(key, default)

    def __eq__(self, other):
        if isinstance(other, dict):
            return self._slice_value == other
        if isinstance(other, CursorSlice):
            # noinspection PyProtectedMember
            return self._slice_value == other._slice_value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class PartitionSlice(DeclarativeStreamSlice):
    def __init__(self, partition_value):
        self._partition_value = partition_value

    @property
    def partition(self):
        return self._partition_value

    @property
    def cursor_slice(self):
        return {}

    def __repr__(self):
        return repr(self._partition_value)

    def __setitem__(self, key: str, value: Any):
        raise ValueError("PartitionSlice is immutable")

    def __getitem__(self, key: str):
        return self._partition_value[key]

    def __len__(self):
        return len(self._partition_value)

    def __iter__(self):
        return iter(self._partition_value)

    def __contains__(self, item: str):
        return item in self._partition_value

    def keys(self):
        return self._partition_value.keys()

    def items(self):
        return self._partition_value.items()

    def values(self):
        return self._partition_value.values()

    def get(self, key: str, default: Any) -> Any:
        return self._partition_value.get(key, default)

    def __eq__(self, other):
        if isinstance(other, dict):
            return self._partition_value == other
        if isinstance(other, PartitionSlice):
            # noinspection PyProtectedMember
            return self._partition_value == other._partition_value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
