#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Iterable

from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition


class PartitionGenerator(ABC):
    @abstractmethod
    def generate(self) -> Iterable[Partition]:
        """
        Generates partitions for a given sync mode.
        :return: An iterable of partitions
        """
        pass
