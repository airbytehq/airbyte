#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
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

class ConcurrencyPolicy:
    async def acquire(self) -> bool:
        pass

class StaticConcurrencyPolicy(ConcurrencyPolicy):

    def __init__(self, max_workers: int):
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
    async def acquire(self) -> bool:
        return await self.semaphore.acquire()

async def request_consumer(queue, output_queue, semaphore: asyncio.Semaphore):
    # Simulate consuming items
    i = 0
    while not queue.empty():
        # Check if the consumer wants to produce an item
        # This needs to check if it can run...
        print(f"request consumer waiting for semaphore {i}")
        # The semaphore is essentially how we can control concurrency and rate limit
        async with semaphore:
            print(f"request consumer acquired semaphore {i}")
            item = await queue.get()
            task = item[1]

            print(f"request consumer reading {task}")

            record_task = RecordsTask(partition=task.partition, records=[i for i in range(task.partition + task.request)])
            await output_queue.put((task.partition, record_task))

            # If there is a next_page_token, add the next request to submit to the task queue
            if should_produce(task):
                new_task = RequestTask(request=task.request+1, partition=task.partition, has_next=False)
                i+=1
                await queue.put((task.partition, new_task))
                print(f'Produced by consumer: {item}')

            # Consume items from the queue
            await asyncio.sleep(5)

async def record_consumer(queue):
    # Simulate consuming items
    while True:
        # Consume items from the queue
        priority, item = await queue.get()
        print(f'Consumed: {item}')
def should_produce(task):
    return task.has_next

async def main():
    request_queue = asyncio.PriorityQueue()
    records_queue = asyncio.PriorityQueue()
    max_workers = 2
    semaphore = asyncio.Semaphore(max_workers)
    num_partitions = 10
    # Add one task per partition (the first request to submit)
    for i in range(num_partitions):
        item = (i, RequestTask(request=1, partition=i, has_next=True))
        await request_queue.put(item)
        print(f'Produced: {item}')

    # Start the producer and consumer coroutines
    tasks = [
        # Initially create one task per partition
        *[asyncio.create_task(request_consumer(request_queue, records_queue, semaphore)) for _ in range(num_partitions)],
        asyncio.create_task(record_consumer(records_queue)),
    ]

    # Wait for all tasks to complete
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
