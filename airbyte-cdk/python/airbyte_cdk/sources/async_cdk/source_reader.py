import asyncio
import logging
from queue import Queue
from threading import Thread
from typing import Any, Callable, Dict, Iterator

import aiohttp

DEFAULT_TIMEOUT = None


class Sentinel:
    def __init__(self, name: str):
        self.name = name


class SourceReader(Iterator):
    def __init__(self, logger: logging.Logger, queue: Queue, sentinels: Dict[str, Sentinel], reader_fn: Callable, *args: Any):
        self.logger = logger
        self.queue = queue
        self.sentinels = sentinels
        self.reader_fn = reader_fn
        self.reader_args = args
        self.sessions: Dict[str, aiohttp.ClientSession] = {}

        self.thread = Thread(target=self._start_reader_thread)
        self.thread.start()

    def _start_reader_thread(self):
        asyncio.run(self.reader_fn(*self.reader_args))

    def __next__(self):
        loop = asyncio.get_event_loop()
        try:
            item = self.queue.get(timeout=DEFAULT_TIMEOUT)
            if isinstance(item, Exception):
                self.logger.error(f"An error occurred in the async thread: {item}")
                self.thread.join()
                raise item
            if isinstance(item, Sentinel):
                # Sessions can only be closed once items in the stream have all been dequeued
                if session := self.sessions.pop(item.name, None):
                    loop.create_task(session.close())  # TODO: this can be done better
                try:
                    self.sentinels.pop(item.name)
                except KeyError:
                    raise RuntimeError(f"The sentinel for stream {item.name} was already dequeued. This is unexpected and indicates a possible problem with the connector. Please contact Support.")
                if not self.sentinels:
                    self.thread.join()
                    raise StopIteration
                else:
                    return self.__next__()
            else:
                return item
        finally:
            loop.create_task(self.cleanup())

    def drain(self):
        while not self.queue.empty():
            yield self.queue.get()
        self.thread.join()

    async def cleanup(self):
        for session in self.sessions.values():
            await session.close()
