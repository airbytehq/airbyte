#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping


class Record:
    """
    Represents a record read from a stream.
    """

    def __init__(self, stream_data: Mapping[str, Any]):
        self.stream_data = stream_data

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Record):
            return False
        return self.stream_data == other.stream_data

    def __str__(self):
        return str(self.stream_data)
