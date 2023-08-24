from queue import Queue

from airbyte_cdk.sources.streams import Stream


class PartitionGenerator:
    def __init__(self, queue: Queue):
        self._queue = queue

    def generate_partitions_for_stream(self, stream: Stream, executor):
        print("generate_partitions_for_stream")
        all_partitions = []
        for partition in stream.generate_partitions(executor):
            print(f"putting partition and stream on queue for {partition}. stream: {stream.name}")
            self._queue.put((partition, stream))
            all_partitions.append(partition)
        return all_partitions
