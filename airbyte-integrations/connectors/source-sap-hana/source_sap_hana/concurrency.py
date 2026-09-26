# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Runs several message generators on worker threads and interleaves their output into one iterator."""

from __future__ import annotations

import queue
import threading
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar


T = TypeVar("T")

_DONE = object()


def interleave(producers: list[Callable[[], Iterator[T]]], max_workers: int, buffer_size: int = 1000) -> Iterator[T]:
    """Yields items from all producers as they arrive, running at most `max_workers` producers at once.

    Each producer's own items stay in order. The bounded buffer applies backpressure, so a slow consumer
    (the Airbyte platform reading stdout) never makes the workers load whole tables into memory. If the
    consumer stops early, or a producer raises, the other workers are told to stop and are waited for.
    """
    buffer: queue.Queue[object] = queue.Queue(maxsize=buffer_size)
    stop = threading.Event()

    def put(item: object) -> bool:
        while not stop.is_set():
            try:
                buffer.put(item, timeout=0.2)
                return True
            except queue.Full:
                continue
        return False

    def run(producer: Callable[[], Iterator[T]]) -> None:
        try:
            for item in producer():
                if not put(item):
                    return
        except Exception as error:  # noqa: BLE001 - re-raised in the consumer thread
            put(_Failure(error))
        finally:
            put(_DONE)

    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="stream-reader") as pool:
        for producer in producers:
            pool.submit(run, producer)
        remaining = len(producers)
        try:
            while remaining:
                item = buffer.get()
                if item is _DONE:
                    remaining -= 1
                elif isinstance(item, _Failure):
                    raise item.error
                else:
                    yield item  # type: ignore[misc]
        finally:
            stop.set()


class _Failure:
    def __init__(self, error: BaseException):
        self.error = error
