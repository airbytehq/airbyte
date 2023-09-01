#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Iterable

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.partitions.partition import Partition


class PartitionGenerator(ABC):
    @abstractmethod
    def generate(self, sync_mode: SyncMode) -> Iterable[Partition]:
        # FIXME: Pass the state here when add support for incremental
        pass
