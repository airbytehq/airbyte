#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from queue import Queue

from airbyte_cdk.sources.streams import Stream


class PartitionGenerator:
    def __init__(self, queue: Queue, name: str):
        self._queue = queue
        self._name = name

    def generate_partitions_for_stream(self, stream: Stream, executor):
        print(f"generate_partitions_for_stream for {self._name} for stream {stream.name}")
        all_partitions = []
        for partition in stream.generate_partitions(executor):
            print(f"putting partition and stream on queue for {partition}. stream: {stream.name}")
            self._queue.put((partition, stream))
            all_partitions.append(partition)
        print(f"{self._name} is done generating partitions for stream {stream.name}. returning from task")
        return all_partitions
