import asyncio
import concurrent.futures
import threading
from asyncio import AbstractEventLoop
from typing import TypeVar, AsyncIterable, Iterable
import queue

T = TypeVar("T")
SENTINEL_VALUE = None


def run_async_gen_in_thread(loop: AbstractEventLoop, async_gen: AsyncIterable[T], q: queue.Queue):
    """
    Run an async generator in the specified event loop, putting results onto the queue `q`.
    """

    async def main():
        async for value in async_gen:
            if value == SENTINEL_VALUE:
                raise ValueError(f"Received sentinel value {SENTINEL_VALUE} while reading the input generator.")
            q.put(value)

        # Put a sentinel value on the queue to indicate that the generator is exhausted
        q.put(SENTINEL_VALUE)

    loop.run_until_complete(main())


def consume_async_iterable(gen: AsyncIterable[T]) -> Iterable[T]:
    # Creating a new event loop in the separate thread is necessary because each thread can have at most one event loop, and by default
    # the main thread will already have one if asyncio is being used there. Since we're running asyncio code in a separate thread,
    # we need to create a new event loop for that thread.
    # TODO I'm not sure we need a new event loop tbh
    q = queue.Queue()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        loop = asyncio.new_event_loop()
        future = executor.submit(run_async_gen_in_thread, loop, gen, q)
        while True:
            # raise an error if it has occurred

            try:
                if future.done():
                    future.result()
                next_value = q.get(timeout=1)
                if next_value == SENTINEL_VALUE:
                    break
                yield next_value
            except queue.Empty:
                pass
