#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition


class Record:
    """
    Represents a record read from a stream.
    """

    def __init__(self, data: Mapping[str, Any], partition: "Partition"):
        self.data = data
        self.partition = partition

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Record):
            return False
        return self.data == other.data and self.partition.stream_name() == other.partition.stream_name()

    def __repr__(self) -> str:
        return f"Record(data={self.data}, stream_name={self.partition.stream_name()})"
