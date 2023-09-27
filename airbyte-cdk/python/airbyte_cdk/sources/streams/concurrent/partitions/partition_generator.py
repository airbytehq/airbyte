#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import copy
import json
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Optional, Tuple, Union

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
        for record_data in self._stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=copy.deepcopy(self._slice)):
            yield Record(record_data)

    # def __eq__(self, other: Any) -> bool:
    #     if not isinstance(other, LegacyPartition):
    #         return False
    #     return _make_hash(self._slice) == _make_hash(other._slice) and self._stream.name == other._stream.name

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return self._slice

    def __hash__(self) -> int:

        if self._slice:
            s = json.dumps(self._slice, sort_keys=True, separators=(",", ":"))
            print(s)
            print(hash(s))
            return hash((self._stream.name, s))
        else:
            return hash(self._stream.name)

    def __repr__(self):
        return f"LegacyPartition({self._stream.name}, {self._slice})"


def _make_hash(o) -> Union[Tuple[Any, ...], int]:
    """
    Makes a hash from a dictionary, list, tuple or set to any level, that contains
    only other hashable types (including any lists, tuples, sets, and
    dictionaries).
    """
    # print(f"o: {o}. type: {type(o)}")
    if isinstance(o, str):
        return hash(o)
    if isinstance(o, dict):
        new_o = copy.deepcopy(o)
        for k, v in new_o.items():
            new_o[k] = _make_hash(v)
        h = hash(tuple(frozenset(sorted(new_o.items()))))
    elif isinstance(o, Iterable):
        h = tuple([_make_hash(e) for e in o])
    else:
        h = hash(o)
    print(f"hash: {h} for {o}")
    return h


class LegacyPartitionGenerator(PartitionGenerator):
    def __init__(self, stream: Stream):
        self._stream = stream

    def generate(self, sync_mode: SyncMode) -> Iterable[Partition]:
        # return [LegacyPartition(self._stream, _slice) for _slice in self._stream.stream_slices(sync_mode=sync_mode)]
        for s in self._stream.stream_slices(sync_mode=sync_mode):
            yield LegacyPartition(self._stream, copy.deepcopy(s))
