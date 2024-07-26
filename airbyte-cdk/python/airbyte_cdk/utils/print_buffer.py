# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys
import time
from io import StringIO
from threading import RLock
from types import TracebackType
from typing import Optional


class PrintBuffer:
    def __init__(self, flush_interval: float = 0.1):
        self.buffer = StringIO()
        self.flush_interval = flush_interval
        self.last_flush_time = time.monotonic()
        self.lock = RLock()

    def write(self, message: str) -> None:
        with self.lock:
            self.buffer.write(message)
            current_time = time.monotonic()
            if (current_time - self.last_flush_time) >= self.flush_interval:
                self.flush()
                self.last_flush_time = current_time

    def flush(self) -> None:
        with self.lock:
            combined_message = self.buffer.getvalue()
            sys.__stdout__.write(combined_message)  # type: ignore[union-attr]
            self.buffer = StringIO()

    def __enter__(self) -> "PrintBuffer":
        self.old_stdout = sys.stdout
        sys.stdout = self
        return self

    def __exit__(self, exc_type: Optional[BaseException], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> None:
        self.flush()
