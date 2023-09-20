#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.record import Record


class Partition(ABC):
    @abstractmethod
    def read(self) -> Iterable[Record]:
        pass

    @abstractmethod
    def to_slice(self) -> Mapping[str, Any]:
        pass


class LegacyPartition(Partition):
    def __init__(self, stream: Stream, _slice: Optional[Mapping[str, Any]]):
        self._stream = stream
        self._slice = _slice

    def read(self) -> Iterable[Record]:
        for record_data in self._stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=self._slice):
            yield Record(record_data)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, LegacyPartition):
            return False
        return self._slice == other._slice and self._stream == other._stream

    def to_slice(self) -> Mapping[str, Any]:
        return self._slice
