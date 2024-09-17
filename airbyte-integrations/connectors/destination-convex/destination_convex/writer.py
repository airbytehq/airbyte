#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time
from collections.abc import Mapping
from typing import Any, List

from destination_convex.client import ConvexClient


class ConvexWriter:
    """
    Buffers messages before sending them to Convex.
    """

    write_buffer: List[Mapping[str, Any]] = []
    flush_interval = 1000

    def __init__(self, client: ConvexClient):
        self.client = client

    def delete_tables(self, table_names: List[str]) -> None:
        """Deletes all the records belonging to the input stream"""
        if len(table_names) > 0:
            self.client.delete(table_names)

    def add_indexes(self, indexes: Mapping[str, List[List[str]]]) -> None:
        self.client.add_primary_key_indexes(indexes)
        self.__poll_for_indexes(indexes)

    def __poll_for_indexes(self, indexes: Mapping[str, List[List[str]]]) -> None:
        """Polls until the indexes specified are ready"""
        tables = list(indexes.keys())
        while True:
            resp = self.client.primary_key_indexes_ready(tables)
            if resp.json()["indexesReady"]:
                break
            else:
                time.sleep(1)
        return

    def queue_write_operation(self, message: Mapping[str, Any]) -> None:
        """Adds messages to the write queue and flushes if the buffer is full"""
        self.write_buffer.append(message)
        if len(self.write_buffer) == self.flush_interval:
            self.flush()

    def flush(self) -> None:
        """Writes to Convex"""

        self.client.batch_write(self.write_buffer)
        self.write_buffer.clear()
