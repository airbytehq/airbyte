# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys
from io import StringIO
from threading import Lock
from types import TracebackType
from typing import Optional


class PrintBuffer:
    """
    A class to buffer print statements and flush them at a specified interval.

    The PrintBuffer class is designed to capture and buffer output that would
    normally be printed to the standard output (stdout). This can be useful for
    scenarios where you want to minimize the number of I/O operations by grouping
    multiple print statements together and flushing them as a single operation.

    Attributes:
        buffer (StringIO): A buffer to store the messages before flushing.
        lock (Lock): A lock to ensure thread-safe operations.

    Methods:
        write(message: str) -> None:
            Writes a message to the buffer.

        flush() -> None:
            Flushes the buffer content to the standard output.

        __enter__() -> "PrintBuffer":
            Enters the runtime context related to this object, redirecting stdout and stderr.

        __exit__(exc_type, exc_val, exc_tb) -> None:
            Exits the runtime context and restores the original stdout and stderr.
    """

    def __init__(self):
        self.buffer = StringIO()
        self.lock = Lock()

    def write(self, message: str) -> None:
        with self.lock:
            self.buffer.write(message)

    def flush(self) -> None:
        with self.lock:
            combined_message = self.buffer.getvalue()
            sys.__stdout__.write(combined_message)  # type: ignore[union-attr]
            self.buffer = StringIO()

    def __enter__(self) -> "PrintBuffer":
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        # Used to disable buffering during the pytest session, because it is not compatible with capsys
        if "pytest" not in str(type(sys.stdout)).lower():
            sys.stdout = self
            sys.stderr = self
        return self

    def __exit__(self, exc_type: Optional[BaseException], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> None:
        self.flush()
        sys.stdout, sys.stderr = self.old_stdout, self.old_stderr
