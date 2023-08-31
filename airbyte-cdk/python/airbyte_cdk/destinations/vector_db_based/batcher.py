#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Callable, List


class Batcher:
    """
    Batcher is a helper class that batches items and flushes them when the batch size is reached.

    It is used to batch records before writing them to the destination to make the embedding and loading process more efficient.
    The Writer class uses the Batcher class to internally batch records before writing them to the destination - in most cases you don't need to use it directly,
    except if you want to implement a custom writer.
    """

    def __init__(self, batch_size: int, flush_handler: Callable[[List[Any]], None]):
        self.batch_size = batch_size
        self.buffer: List[Any] = []
        self.flush_handler = flush_handler

    def add(self, item: Any) -> None:
        self.buffer.append(item)
        self._flush_if_necessary()

    def flush(self) -> None:
        if len(self.buffer) == 0:
            return
        self.flush_handler(list(self.buffer))
        self.buffer.clear()

    def _flush_if_necessary(self) -> None:
        if len(self.buffer) >= self.batch_size:
            self.flush()
