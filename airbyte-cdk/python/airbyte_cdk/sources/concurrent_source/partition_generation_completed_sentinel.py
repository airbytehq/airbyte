#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.availability_strategy import StreamAvailability


class PartitionGenerationCompletedSentinel:
    """
    A sentinel object indicating all partitions for a stream were produced.
    Includes a pointer to the stream that was processed.
    """

    def __init__(self, stream: AbstractStream, stream_availability: StreamAvailability):
        """
        :param stream: The stream that was processed
        :param stream_availability: The stream availability
        """
        self.stream = stream
        self.stream_availability = stream_availability
