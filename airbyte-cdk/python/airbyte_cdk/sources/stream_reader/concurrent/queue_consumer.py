#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import threading
from queue import Empty, Queue
from typing import List, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.stream_reader.concurrent.record import Record
from airbyte_cdk.sources.stream_reader.concurrent.stream_partition import StreamPartition

_SENTINEL = None


class QueueConsumer:
    def __init__(self, name: str, output_queue: Queue[Optional[Record]]):
        self._name = name
        self._output_queue = output_queue

    def consume_from_queue(self, queue: Queue[Optional[StreamPartition]]) -> List[Record]:
        current_thread = threading.current_thread().ident
        print(f"consume from queue {self._name} from {current_thread}")
        records_and_streams: List[Record] = []
        while True:
            try:
                stream_partition = queue.get(timeout=2)
                if stream_partition is None:
                    print(f"found sentinel for {self._name} from {current_thread}")
                    return records_and_streams
                else:
                    print(f"partition_and_stream for {self._name}: {stream_partition} from {current_thread}")
                    for record in stream_partition.stream.read_records(
                        stream_slice=stream_partition.slice, sync_mode=SyncMode.full_refresh, cursor_field=stream_partition.cursor_field
                    ):
                        self._output_queue.put(Record(record, stream_partition))
                        # records_and_streams.append(Record(record, stream_partition))
                    print(f"{self._name} done reading partition {stream_partition} from {current_thread}")
            except Empty:
                print(f"queue {self._name} is empty from {current_thread}")
