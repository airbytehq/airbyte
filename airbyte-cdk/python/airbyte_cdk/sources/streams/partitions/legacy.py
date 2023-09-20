#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Iterable, Mapping, Optional, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.abstract_stream import AbstractAvailabilityStrategy
from airbyte_cdk.sources.streams.partitions.partition import Partition
from airbyte_cdk.sources.streams.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.record import Record


# FIXME this belongs in a separate module
class LegacyAvailabilityStrategy(AbstractAvailabilityStrategy):
    def __init__(self, stream: Stream, source: Source):
        self._stream = stream
        self._source = source

    def check_availability(self, logger: logging.Logger) -> Tuple[bool, Optional[str]]:
        return self._stream.availability_strategy.check_availability(self._stream, logger, self._source)


class LegacyPartitionGenerator(PartitionGenerator):
    def __init__(self, stream: Stream):
        self._stream = stream

    def generate(self, sync_mode: SyncMode) -> Iterable[Partition]:
        return [LegacyPartition(self._stream, _slice) for _slice in self._stream.stream_slices(sync_mode=sync_mode)]


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
