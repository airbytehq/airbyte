#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream


class StreamReader:
    # FIXME: a lot of the code can probably be shared with the PartitionEnqueuer and PartitionReader
    def __init__(self, queue, sentinel) -> None:
        self._queue = queue
        self._sentinel = sentinel

    def read_from_stream(self, stream: AbstractStream) -> None:
        # print(f"reading from stream: {stream.name}")
        try:
            for record in stream._abstract_stream.read():
                # print(f"adding record to queue {record}")
                self._queue.put(record)
            self._queue.put(self._sentinel)
        except Exception as e:
            # print(f"exception: {e}")
            self._queue.put(e)
