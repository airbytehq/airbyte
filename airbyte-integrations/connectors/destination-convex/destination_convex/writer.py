#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from collections import Mapping
from typing import List

from destination_convex.client import ConvexClient


class ConvexWriter:
    """
    Buffers messages before sending them to Convex.
    """

    write_buffer = []
    flush_interval = 1000

    def __init__(self, client: ConvexClient):
        self.client = client
        self.stream_metadata = None

    def delete_stream_entries(self, stream_names: List[str]):
        """Deletes all the records belonging to the input stream"""
        if len(stream_names) > 0:
            self.client.delete(stream_names)

    def queue_write_operation(self, message: Mapping):
        """Adds messages to the write queue and flushes if the buffer is full"""
        self.write_buffer.append(message)
        if len(self.write_buffer) == self.flush_interval:
            self.flush()

    def flush(self):
        """Writes to Convex"""
        if self.stream_metadata is None:
            raise Exception("Stream metadata must be added before flushing.")
        self.client.batch_write(self.write_buffer, self.stream_metadata)
        self.write_buffer.clear()
