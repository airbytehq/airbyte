#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent.futures
import logging
import os
import sys
import time
from abc import ABC
from queue import Queue
from threading import Semaphore
from typing import Any, Iterator, List, Mapping, MutableMapping, Union

from airbyte_cdk.models import AirbyteCatalog, AirbyteConnectionStatus, AirbyteMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.concurrent.partition_generator import PartitionGenerator
from airbyte_cdk.sources.concurrent.queue_consumer import _SENTINEL, QueueConsumer


class Partition:
    pass


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

    def _get_num_dedicated_consumer_worker(self):
        return max(self._max_workers - 4, 1)

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
        for stream in streams:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers + 10, thread_name_prefix="workerpool") as executor:
                start_time = time.time()
                print(f"generating partitions for stream: {stream.name}")
                # Submit partition generation tasks
                f = executor.submit(PartitionGenerator.generate_partitions_for_stream, self._partitions_generator, stream, executor)
                partition_generation_futures.append(f)

                # Submit record generator tasks
                for i in range(self._get_num_dedicated_consumer_worker()):  # FIXME?
                    f = executor.submit(QueueConsumer.consume_from_queue, self._queue_consumer, self._queue, executor)
                    queue_consumer_futures.append(f)

                # Wait for all partitions to be generated
                done, unfinished = concurrent.futures.wait(partition_generation_futures)

                # Then put the sentinel on the queue
                print("putting sentinel on queue because the source generated all partitions")
                for _ in range(self._get_num_dedicated_consumer_worker()):
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
                print(f"Read {record_counter} records for {stream.name}")
