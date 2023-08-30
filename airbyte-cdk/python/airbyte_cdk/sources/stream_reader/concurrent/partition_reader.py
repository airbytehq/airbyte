#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import threading
from queue import Empty, Queue
from typing import Iterable, List, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.stream_reader.concurrent.record import Record
from airbyte_cdk.sources.stream_reader.concurrent.stream_partition import StreamPartition

_SENTINEL = None


class PartitionReader:
    def __init__(self, name: str, output_queue: Queue[Optional[Record]]):
        self._name = name
        self._output_queue = output_queue

    def process_partition(self, partition: StreamPartition) -> None:
        print(f"{self._name} is processing partition={partition}")
        for record in partition.stream.read_records(
            stream_slice=partition.slice, sync_mode=SyncMode.full_refresh, cursor_field=partition.cursor_field
        ):
            record = Record(record, partition)
            self._output_queue.put(record)
