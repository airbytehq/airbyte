#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Any

from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream


class PartitionGenerationCompletedSentinel:
    """
    A sentinel object indicating all partitions for a stream were produced.
    Includes a pointer to the stream that was processed.
    """

    def __init__(self, stream: AbstractStream, has_generated_partition: bool):
        """
        :param stream: The stream that was processed
        """
        self.stream = stream
        self._has_generated_partition = has_generated_partition

    @property
    def has_generated_partition(self) -> bool:
        return self._has_generated_partition

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, PartitionGenerationCompletedSentinel):
            return self.stream == other.stream
        return False
