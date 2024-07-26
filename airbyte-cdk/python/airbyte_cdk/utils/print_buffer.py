# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import time
from io import StringIO
import sys
from threading import RLock


class PrintBuffer:
    def __init__(self, flush_interval=0.1):
        self.buffer = StringIO()
        self.flush_interval = flush_interval
        self.last_flush_time = time.monotonic()
        self.lock = RLock()

    def write(self, message):
        with self.lock:
            self.buffer.write(message)
            current_time = time.monotonic()
            if (current_time - self.last_flush_time) >= self.flush_interval:
                self.flush()
                self.last_flush_time = current_time

    def flush(self):
        with self.lock:
            combined_message = self.buffer.getvalue()
            sys.__stdout__.write(combined_message)
            self.buffer = StringIO()

    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
