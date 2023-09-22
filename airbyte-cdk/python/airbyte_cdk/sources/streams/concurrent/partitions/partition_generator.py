#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import copy
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record


class PartitionGenerator(ABC):
    @abstractmethod
    def generate(self, sync_mode: SyncMode) -> Iterable[Partition]:
        """
        Generates partitions for a given sync mode.
        :param sync_mode: SyncMode
        :return:
        """
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

    def __hash__(self):
        if self._slice:
            return hash((self._stream.name, make_hash(self._slice)))
        else:
            return hash(self._stream.name)


def make_hash(o):

    """
    Makes a hash from a dictionary, list, tuple or set to any level, that contains
    only other hashable types (including any lists, tuples, sets, and
    dictionaries).
    """

    if isinstance(o, (set, tuple, list)):

        return tuple([make_hash(e) for e in o])

    elif not isinstance(o, dict):

        return hash(o)

    new_o = copy.deepcopy(o)
    for k, v in new_o.items():
        new_o[k] = make_hash(v)


class LegacyPartitionGenerator(PartitionGenerator):
    def __init__(self, stream: Stream):
        self._stream = stream

    def generate(self, sync_mode: SyncMode) -> Iterable[Partition]:
        # return [LegacyPartition(self._stream, _slice) for _slice in self._stream.stream_slices(sync_mode=sync_mode)]
        for s in self._stream.stream_slices(sync_mode=sync_mode):
            yield LegacyPartition(self._stream, s)
