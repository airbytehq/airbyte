#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent.futures
import logging
from abc import ABC
from queue import Empty, Queue
from typing import Any, Iterator, List, Mapping, MutableMapping, Union

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    SyncMode,
)
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream


class Partition:
    pass


_SENTINEL = ("SENTINEL", "SENTINEL")


class PartitionGenerator:
    def __init__(self, queue: Queue):
        self._queue = queue

    def generate_partitions_for_stream(self, stream: Stream):
        print("generate_partitions_for_stream")
        for partition in stream.generate_partitions():
            print("putting partition and stream on queue...")
            self._queue.put((partition, stream))


class QueueConsumer:
    def __init__(self):
        self._iterations = 0

    def consume_from_queue(self, queue: Queue):
        print("consume from queue")
        while True:
            self._iterations += 1
            if self._iterations >= 10:
                raise RuntimeError("Iterating for too long")
            try:
                partition_and_stream = queue.get(timeout=2)
                if partition_and_stream == _SENTINEL:
                    print("found sentinel")
                    break
                else:
                    print(f"partition_and_stream: {partition_and_stream}")
                    partition, stream = partition_and_stream
                    # cursor_field = None
                    # stream_slice = None
                    yield from stream.read_records(SyncMode.full_refresh)
            except Empty:
                print("queue is empty")


class ConcurrentAbstractSource(AbstractSource, ABC):
    def __init__(self, partitions_generator: PartitionGenerator, queue_consumer: QueueConsumer, queue: Queue, max_workers: int):
        self._partitions_generator = partitions_generator
        self._queue_consumer = queue_consumer
        self._queue = queue
        self._max_workers = max_workers

    # FIXME: can we safely replace Mappings with types?
    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Implements the Discover operation from the Airbyte Specification.
        See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#discover.
        """
        pass

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Implements the Check Connection operation from the Airbyte Specification.
        See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#check.
        """
        pass

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Iterator[AirbyteMessage]:
        # FIXME: what's the deal with the split config?
        # config, internal_config = split_config(config)
        streams = self.streams(config)
        print("read")
        partition_generation_futures = []
        queue_consumer_futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            for stream in streams:
                # Submit partition generation tasks
                f = executor.submit(PartitionGenerator.generate_partitions_for_stream, self._partitions_generator, stream)
                partition_generation_futures.append(f)

            # Submit record generator tasks
            for i in range(self._max_workers):  # FIXME?
                f = executor.submit(QueueConsumer.consume_from_queue, self._queue_consumer, self._queue)
                queue_consumer_futures.append(f)

            # Wait for all partitions to be generated
            concurrent.futures.wait(partition_generation_futures)
            # Then put the sentinel on the queue
            print("putting sentinel on queue")
            self._queue.put(_SENTINEL)

            # Wait for the consumers to finish
            # FIXME: We should start yielding as soon as the first ones are done...
            done, unfinished = concurrent.futures.wait(queue_consumer_futures)
            print(f"done: {done}")
            print(f"unfinished: {unfinished}")
            for future in done:
                # Each result is an iterable of record
                result = future.result()
                print(f"result: {result}")
                for partition_record in result:
                    yield partition_record
