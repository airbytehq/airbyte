#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod
from typing import Iterable

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition


class PartitionGenerator(ABC):
    @abstractmethod
    def generate(self, sync_mode: SyncMode) -> Iterable[Partition]:
        """
                Generates partitions for a given sync mode.
                :param sync_mode: SyncMode
        <<<<<<< HEAD
                :return: An iterable of partitions.
        =======
                :return: An iterable of partitions
        >>>>>>> alex/abstract_stream
        """
        pass
