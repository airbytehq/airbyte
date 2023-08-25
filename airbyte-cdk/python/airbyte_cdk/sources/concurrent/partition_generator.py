#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from queue import Queue

from airbyte_cdk.sources.streams import Stream


class PartitionGenerator:
    def __init__(self, queue: Queue, name: str):
        self._queue = queue
        self._name = name

    def generate_partitions_for_stream(self, stream: Stream, sync_mode, cursor_field):
        print(f"generate_partitions_for_stream for {self._name} for stream {stream.name}")
        for partition in stream.generate_partitions(sync_mode=sync_mode, cursor_field=cursor_field):
            print(f"putting partition and stream on queue for {partition}. stream: {stream.name}")
            self._queue.put((partition, stream))
            yield partition  # FIXME: Why is this needed?
