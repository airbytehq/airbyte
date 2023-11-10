#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream


class StreamCompleteSentinel:
    """
    A sentinel object indicating all records for a partition were produced.
    Includes a pointer to the partition that was processed.
    """

    def __init__(self, stream: AbstractStream):
        """
        :param stream: The stream that was processed
        """
        self.stream = stream
