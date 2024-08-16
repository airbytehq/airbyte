#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping


class Record:
    """
    Represents a record read from a stream.
    """

    def __init__(self, data: Mapping[str, Any], partition):
        self.data = data
        self.partition = partition

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Record):
            return False
        return self.data == other.data and self.stream_name == other.stream_name

    def __repr__(self) -> str:
        return f"Record(data={self.data}, stream_name={self.partition.stream_name()})"
