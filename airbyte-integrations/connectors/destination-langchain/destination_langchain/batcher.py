#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from collections.abc import Callable
from typing import Any


class Batcher:
    def __init__(self, batch_size: int, flush_handler: Callable[[list[Any]], None]):
        self.batch_size = batch_size
        self.buffer = []
        self.flush_handler = flush_handler

    def add(self, item: Any):
        self.buffer.append(item)
        self._flush_if_necessary()

    def flush(self):
        if len(self.buffer) == 0:
            return
        self.flush_handler(list(self.buffer))
        self.buffer.clear()

    def _flush_if_necessary(self):
        if len(self.buffer) >= self.batch_size:
            self.flush()
