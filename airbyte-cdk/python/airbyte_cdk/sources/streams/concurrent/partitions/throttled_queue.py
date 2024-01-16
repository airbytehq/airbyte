# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from queue import Queue

from airbyte_cdk.sources.concurrent_source.throttler import Throttler
from airbyte_cdk.sources.streams.concurrent.partitions.types import QueueItem


class ThrottledQueue:
    """
    A queue that throttles the number of items that can be added to it.
    """

    def __init__(self, queue: Queue[QueueItem], throttler: Throttler, timeout: float) -> None:
        """
        :param queue: The queue to throttle
        :param throttler: The throttler to use to throttle the queue
        :param timeout: The timeout to use when getting items from the queue
        """
        self._queue = queue
        self._throttler = throttler
        self._timeout = timeout

    def put(self, item: QueueItem) -> None:
        self._throttler.wait_and_acquire()
        self._queue.put(item)

    def get(self) -> QueueItem:
        return self._queue.get(block=True, timeout=self._timeout)

    def empty(self) -> bool:
        return self._queue.empty()
