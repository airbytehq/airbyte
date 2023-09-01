#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


class StreamPartition:
    def __str__(self) -> str:
        return f"StreamPartition(stream={self._stream.name}, slice={self._slice}, cursor_field={self._cursor_field})"

    def __init__(self, stream: Stream, _slice: Optional[Mapping[str, Any]], cursor_field: Optional[List[str]]):
        self._stream = stream
        self._slice = _slice
        self._cursor_field = cursor_field

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StreamPartition):
            return False
        return self._slice == other._slice and self._stream == other._stream

    def read(self):
        # FIXME: Only full refresh is supported for now
        # FIXME: User-defined cursor fields are not supported for now
        yield from self._stream.read_records(SyncMode.full_refresh, cursor_field=self._cursor_field, stream_slice=self._slice)

    def get_logger(self):
        return self._stream.logger
