#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue
from typing import Iterable, List, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.stream_reader.concurrent.stream_partition import StreamPartition
from airbyte_cdk.sources.streams import Stream


class PartitionGenerator:
    def __init__(self, queue: Queue[Optional[StreamPartition]], name: str):
        self._queue = queue
        self._name = name

    def generate_partitions_for_stream(self, stream: Stream, sync_mode: SyncMode, cursor_field: Optional[List[str]]) -> None:
        print(f"generate_partitions_for_stream for {self._name} for stream {stream.name}")
        for partition in stream.generate_partitions(sync_mode=sync_mode, cursor_field=cursor_field):
            print(f"putting partition and stream on queue for {partition}. stream: {stream.name}")
            stream_partition = StreamPartition(stream, partition, cursor_field)
            self._queue.put(stream_partition)
