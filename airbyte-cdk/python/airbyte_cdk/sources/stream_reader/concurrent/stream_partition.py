#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

from airbyte_cdk.sources.streams import Stream


class StreamPartition:
    def __str__(self) -> str:
        return f"StreamPartition(stream={self.stream.name}, slice={self.slice}, cursor_field={self.cursor_field})"

    def __init__(self, stream: Stream, _slice: Optional[Mapping[str, Any]], cursor_field: Optional[List[str]]):
        self.stream = stream
        self.slice = _slice
        self.cursor_field = cursor_field

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StreamPartition):
            return False
        return self.slice == other.slice and self.stream == other.stream and self.cursor_field == other.cursor_field
