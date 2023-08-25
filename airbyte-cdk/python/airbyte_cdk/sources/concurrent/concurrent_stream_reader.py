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

    def read_stream(self, stream: Stream):
        all_records = []
        partition_generation_futures = []
        queue_consumer_futures = []
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
            for future in done:
                # Each result is an iterable of record
                result = future.result()
                # print(f"result: {result}")
                for partition_record_and_stream in result:
                    partition_record, stream = partition_record_and_stream
                    # FIXME we should wrap the output in a dataclass!
                    all_records.append((partition_record, stream))
        return all_records

    def _get_num_dedicated_consumer_worker(self) -> int:
        return int(max(self._max_workers / 2, 1))
