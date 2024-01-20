#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, MutableMapping

from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record


class FileBasedNoopCursor(Cursor):
    @property
    def state(self) -> MutableMapping[str, Any]:
        return {}

    def observe(self, record: Record) -> None:
        pass

    def close_partition(self, partition: Partition) -> None:
        pass

    def set_pending_partitions(self, partitions: Iterable[Partition]) -> None:
        pass
