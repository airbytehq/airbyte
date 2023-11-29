#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream


class PartitionGenerationCompletedSentinel:
    """
    A sentinel object indicating all partitions for a stream were produced.
    Includes a pointer to the stream that was processed.
    """

    def __init__(self, stream: AbstractStream):
        """
        :param stream: The stream that was processed
        """
        self.stream = stream
