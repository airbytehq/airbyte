#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator


class PartitionGenerationCompletedSentinel:
    """
    A sentinel object indicating all records for a partition were produced.
    Includes a pointer to the partition that was processed.
    """

    def __init__(self, partition_generator: PartitionGenerator):
        """
        :param partition_generator: The partition_generator that was processed
        """
        self.partition_generator = partition_generator
