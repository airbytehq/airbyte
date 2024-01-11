#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from collections.abc import Mapping
from logging import getLogger
from uuid import uuid4

from meilisearch import Client

logger = getLogger("airbyte")


class MeiliWriter:
    flush_interval = 50000

    def __init__(self, client: Client, stream_name: str, primary_key: str):
        self.client = client
        self.primary_key = primary_key
        self.stream_name: str = stream_name
        self._write_buffer = []

        logger.info(f"Creating MeiliWriter for {self.stream_name}")

    def queue_write_operation(self, data: Mapping):
        random_key = str(uuid4())
        self._write_buffer.append({**data, self.primary_key: random_key})
        if len(self._write_buffer) == self.flush_interval:
            logger.debug(f"Reached limit size: flushing records for {self.stream_name}")
            self.flush()

    def flush(self):
        buffer_size = len(self._write_buffer)
        if buffer_size == 0:
            return
        logger.info(f"Flushing {buffer_size} records")
        response = self.client.index(self.stream_name).add_documents(self._write_buffer)
        self.client.wait_for_task(response.task_uid, 1800000, 1000)
        self._write_buffer.clear()
