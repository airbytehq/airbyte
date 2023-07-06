#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
from abc import abstractmethod, ABC

from airbyte_cdk.entrypoint import launch
import datetime
from source_stripe import SourceStripe
import dataclasses

import asyncio


@dataclasses.dataclass
class RequestTask:
    request: int
    partition: int
    has_next: bool


@dataclasses.dataclass
class RecordsTask:
    partition: int
    records: list

    def __lt__(self, other):
        return self.partition < other.partition


class ConcurrencyPolicy(ABC):
    @abstractmethod
    async def acquire(self) -> bool:
        # Probably needs additional parameters such as the
        pass


class StaticConcurrencyPolicy(ConcurrencyPolicy):

    def __init__(self, max_workers: int):
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)

    async def acquire(self) -> bool:
        return await self.semaphore.acquire()

    async def __aenter__(self):
        await self.acquire()
        return None

    async def __aexit__(self, exc_type, exc, tb):
        self.semaphore.release()


class OneRequestPerSecondPolicy(ConcurrencyPolicy):
    def __init__(self, max_request_per_seconds):
        self.max_request_per_seconds = max_request_per_seconds
        self.semaphore = asyncio.Semaphore(1)
        self._last_request_time = datetime.datetime.now()
        self._request_count = 0

    async def acquire(self) -> bool:
        # FIXME: this method isn't entirely right.
        # I think we want some sort of while loop
        async with self.semaphore:
            now = datetime.datetime.now()
            print(f"acquiring semaphore. last request was at {self._last_request_time}")
            if now - self._last_request_time >= datetime.timedelta(seconds=1):
                self._request_count = 0
            if self._request_count < self.max_request_per_seconds:
                self._request_count += 1
                self._last_request_time = now
                print(f"submitting request")
                return True
            else:
                print(f"last request was too recent. waiting...")
                return False

    async def __aenter__(self):
        await self.acquire()
        return None

    async def __aexit__(self, exc_type, exc, tb):
        pass


async def request_consumer(queue, output_queue, concurrency_policy: ConcurrencyPolicy):
    # Simulate consuming items
    i = 0
    while not queue.empty():
        # Check if the consumer wants to produce an item
        # This needs to check if it can run...
        print(f"request consumer waiting for semaphore")
        # The semaphore is essentially how we can control concurrency and rate limit
        async with concurrency_policy:
            print(f"request consumer acquired semaphore")
            item = await queue.get()
            task = item[1]

            print(f"request consumer reading {task}")

            record_task = RecordsTask(partition=task.partition, records=[i for i in range(task.partition + task.request)])
            await output_queue.put((task.partition, record_task))

            # If there is a next_page_token, add the next request to submit to the task queue
            if should_produce(task):
                new_task = RequestTask(request=task.request + 1, partition=task.partition, has_next=False)
                i += 1
                await queue.put((task.partition, new_task))
                print(f'Produced by consumer: {item}')

            # Consume items from the queue
            await asyncio.sleep(0.1)


async def record_consumer(queue):
    # Simulate consuming items
    while True:
        # Consume items from the queue
        priority, item = await queue.get()
        print(f'Consumed: {item}')


def should_produce(task):
    # We should produce a new request if either
    # 1. The task has a next page token
    # 2. The request failed and can be retried
    return task.has_next


async def main():
    """
    This is an example of a concurrency model based around a producer/active consumer model.

    max_worker: the maximum number of consumers that can run at any given time. This is a static number. I suspect this number is a platform level constraint
    concurrency_policy: answers the question: can the requester submit a request right now?
        - alternative: wait until I can submit a request?
    request_queue: priority queue of requests to submit (ordered

    """
    request_queue = asyncio.PriorityQueue()
    records_queue = asyncio.PriorityQueue()
    max_workers = 2
    # concurrency_policy = StaticConcurrencyPolicy(max_workers=max_workers)
    concurrency_policy = OneRequestPerSecondPolicy(1)
    num_partitions = 10
    semaphore: asyncio.Semaphore = asyncio.Semaphore(max_workers)
    # Add one task per partition (the first request to submit)
    for i in range(num_partitions):
        # We use the partition id as the priority
        # This allows us to finish earlier partitions first instead of round-robining them
        item = (i, RequestTask(request=1, partition=i, has_next=True))
        await request_queue.put(item)
        print(f'Produced: {item}')

    # Start the producer and consumer coroutines
    tasks = [
        # Initially create one task per partition
        *[asyncio.create_task(request_consumer(request_queue, records_queue, concurrency_policy)) for _ in range(num_partitions)],
        asyncio.create_task(record_consumer(records_queue)),
    ]

    # Wait for all tasks to complete
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
