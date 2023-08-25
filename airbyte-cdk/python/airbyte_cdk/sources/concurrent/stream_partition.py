#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Any, Dict, List, Optional

from airbyte_cdk.sources.streams import Stream


class StreamPartition:
    def __init__(self, stream: Stream, _slice: Dict[str, Any], cursor_field: Optional[List[str]]):
        self.stream = stream  # FIXME can we not expose this?
        self.slice = _slice  # FIXME can we make this not a dict?
        self.cursor_field = cursor_field

    def __eq__(self, other):
        if not isinstance(other, StreamPartition):
            return False
        return self.slice == other.slice and self.stream == other.stream and self.cursor_field == other.cursor_field
