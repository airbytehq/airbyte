#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent.futures
import logging
import threading
import time
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
        all_partitions = []
        for partition in stream.generate_partitions():
            print("putting partition and stream on queue...")
            self._queue.put((partition, stream))
            all_partitions.append(partition)
        return all_partitions


class QueueConsumer:
    def __init__(self):
        self._iterations = 0

    def consume_from_queue(self, queue: Queue):
        current_thread = threading.current_thread().ident
        print(f"consume from queue from {current_thread}")
        records_and_streams = []
        while True:
            self._iterations += 1
            try:
                partition_and_stream = queue.get(timeout=2)
                if partition_and_stream == _SENTINEL:
                    print(f"found sentinel from {current_thread}")
                    return records_and_streams
                else:
                    print(f"partition_and_stream: {partition_and_stream} from {current_thread}")
                    partition, stream = partition_and_stream
                    # cursor_field = None
                    # stream_slice = None
                    for record in stream.read_records(SyncMode.full_refresh, stream_slice=partition):
                        records_and_streams.append((record, stream))
                    print(f"done reading partition {partition_and_stream} from {current_thread}")
            except Empty:
                print(f"queue is empty from {current_thread}")


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
        print(f"read with {self._max_workers} workers")
        partition_generation_futures = []
        queue_consumer_futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool") as executor:
            start_time = time.time()
            for stream in streams:
                print(f"generating partitions for stream: {stream.name}")
                # Submit partition generation tasks
                f = executor.submit(PartitionGenerator.generate_partitions_for_stream, self._partitions_generator, stream)
                partition_generation_futures.append(f)

            # Submit record generator tasks
            for i in range(self._max_workers):  # FIXME?
                f = executor.submit(QueueConsumer.consume_from_queue, self._queue_consumer, self._queue)
                queue_consumer_futures.append(f)

            # Wait for all partitions to be generated
            done, unfinished = concurrent.futures.wait(partition_generation_futures)

            # Then put the sentinel on the queue
            print("putting sentinel on queue")
            for _ in range(self._max_workers):
                # FIXME: need a test to verify we put many sentinels..
                self._queue.put(_SENTINEL)
            partitions_are_generated_time = time.time()
            print(f"printing partitions generated. it took {partitions_are_generated_time - start_time}")
            for future in done:
                print(future.result())
            print("done printing partitions")

            # Wait for the consumers to finish
            # FIXME: We should start yielding as soon as the first ones are done...
            done, unfinished = concurrent.futures.wait(queue_consumer_futures)
            print(f"done: {done}")
            print(f"unfinished: {unfinished}")
            record_counter = 0
            for future in done:
                # Each result is an iterable of record
                result = future.result()
                print(f"result: {result}")
                for partition_record_and_stream in result:
                    partition_record, stream = partition_record_and_stream
                    record_counter += 1
                    yield self._get_message(partition_record, stream)
            print(f"Read {record_counter} records")
