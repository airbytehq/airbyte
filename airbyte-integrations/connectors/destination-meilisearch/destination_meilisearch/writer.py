#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from collections.abc import Mapping
from logging import getLogger
from uuid import uuid4

from meilisearch import Client

logger = getLogger("airbyte")


class MeiliWriter:
    write_buffer = []
    flush_interval = 50000

    def __init__(self, client: Client, steam_name: str, primary_key: str):
        self.client = client
        self.steam_name = steam_name
        self.primary_key = primary_key

    def queue_write_operation(self, data: Mapping):
        random_key = str(uuid4())
        self.write_buffer.append({**data, self.primary_key: random_key})
        if len(self.write_buffer) == self.flush_interval:
            self.flush()

    def flush(self):
        buffer_size = len(self.write_buffer)
        if buffer_size == 0:
            return
        logger.info(f"flushing {buffer_size} records")
        response = self.client.index(self.steam_name).add_documents(self.write_buffer)
        self.client.wait_for_task(response.task_uid, 1800000, 1000)
        self.write_buffer.clear()
