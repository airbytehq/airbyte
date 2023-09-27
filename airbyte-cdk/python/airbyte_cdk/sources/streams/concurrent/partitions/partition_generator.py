#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import copy
import json
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
        :return: An iterable of partitions.
        """
        pass


class LegacyPartition(Partition):
    """
    This class acts as an adapter between the new Partition interface and the legacy stream_slice "interface"

    LegacyPartitions are instantiated from a Stream and a stream_slice.

    This class can be used to help enable concurrency on existing connectors without having to rewrite everything as AbstractStream.
    In the long-run, it would be preferable to update the connectors, but we don't have the tooling or need to justify the effort at this time.
    """

    def __init__(self, stream: Stream, _slice: Optional[Mapping[str, Any]]):
        """
        :param stream: The stream to delegate to
        :param _slice: The partition's stream_slice
        """
        self._stream = stream
        self._slice = _slice

    def read(self) -> Iterable[Record]:
        """
        Delegates to stream.read_records with the stream_slice
        """
        for record_data in self._stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=copy.deepcopy(self._slice)):
            yield Record(record_data)

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return self._slice

    def __hash__(self) -> int:
        if self._slice:
            # Convert the slice to a string so that it can be hashed
            s = json.dumps(self._slice, sort_keys=True)
            return hash((self._stream.name, s))
        else:
            return hash(self._stream.name)

    def __repr__(self) -> str:
        return f"LegacyPartition({self._stream.name}, {self._slice})"


class LegacyPartitionGenerator(PartitionGenerator):
    """
    This class acts as an adapter between the new PartitionGenerator and Stream.stream_slices

    This class can be used to help enable concurrency on existing connectors without having to rewrite everything as AbstractStream.
    In the long-run, it would be preferable to update the connectors, but we don't have the tooling or need to justify the effort at this time.
    """

    def __init__(self, stream: Stream):
        """
        :param stream: The stream to delegate to
        """
        self._stream = stream

    def generate(self, sync_mode: SyncMode) -> Iterable[Partition]:
        for s in self._stream.stream_slices(sync_mode=sync_mode):
            yield LegacyPartition(self._stream, copy.deepcopy(s))
