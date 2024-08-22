# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any


class StreamThreadException(Exception):
    def __init__(self, exception: Exception, stream_name: str):
        self._exception = exception
        self._stream_name = stream_name

    @property
    def stream_name(self) -> str:
        return self._stream_name

    @property
    def exception(self) -> Exception:
        return self._exception

    def __str__(self) -> str:
        return f"Exception while syncing stream {self._stream_name}: {self._exception}"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, StreamThreadException):
            return self._exception == other._exception and self._stream_name == other._stream_name
        return False
