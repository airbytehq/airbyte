#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent
import concurrent.futures
import time
from queue import Queue

from airbyte_cdk.sources.concurrent.partition_generator import PartitionGenerator
from airbyte_cdk.sources.concurrent.queue_consumer import _SENTINEL, QueueConsumer
from airbyte_cdk.sources.streams import Stream


class ConcurrentStreamReader:
    def __init__(self, partition_generator: PartitionGenerator, queue_consumer: QueueConsumer, queue: Queue, max_workers: int):
        self._partitions_generator = partition_generator
        self._queue_consumer = queue_consumer
        self._queue = queue
        self._max_workers = max_workers

    def read_stream(self, stream: Stream, cursor_field, internal_config, logger):
        # FIXME do something with the cursor field
        # FIXME do something with the internal config
        partition_generation_futures = []
        queue_consumer_futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers + 10, thread_name_prefix="workerpool") as executor:
            # Submit partition generation tasks
            f = executor.submit(PartitionGenerator.generate_partitions_for_stream, self._partitions_generator, stream, executor)
            partition_generation_futures.append(f)

            # Submit record generator tasks
            for i in range(self._get_num_dedicated_consumer_worker()):  # FIXME?
                f = executor.submit(QueueConsumer.consume_from_queue, self._queue_consumer, self._queue)
                queue_consumer_futures.append(f)

            # Wait for all partitions to be generated
            done, unfinished = concurrent.futures.wait(partition_generation_futures)
            # FIXME: handle done and unifishined

            # Then put the sentinel on the queue
            for _ in range(self._get_num_dedicated_consumer_worker()):
                # FIXME: need a test to verify we put many sentinels..
                self._queue.put(_SENTINEL)
            # Wait for the consumers to finish
            # FIXME: We should start yielding as soon as the first ones are done...
            # FIXME handle done and unfinished
            for future in concurrent.futures.as_completed(queue_consumer_futures):
                # Each result is an iterable of record
                result = future.result()
                for partition_record_and_stream in result:
                    partition_record, stream = partition_record_and_stream
                    yield partition_record

    def _get_num_dedicated_consumer_worker(self) -> int:
        # FIXME figure this out and add a unit test
        return int(max(self._max_workers / 2, 1))
