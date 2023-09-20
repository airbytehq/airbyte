#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Iterable

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.partitions.partition import LegacyPartition, Partition


class PartitionGenerator(ABC):
    @abstractmethod
    def generate(self, sync_mode: SyncMode) -> Iterable[Partition]:
        pass


class LegacyPartitionGenerator(PartitionGenerator):
    def __init__(self, stream: Stream):
        self._stream = stream

    def generate(self, sync_mode: SyncMode) -> Iterable[Partition]:
        return [LegacyPartition(self._stream, _slice) for _slice in self._stream.stream_slices(sync_mode=sync_mode)]
