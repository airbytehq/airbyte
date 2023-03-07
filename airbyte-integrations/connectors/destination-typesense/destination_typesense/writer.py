#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from collections.abc import Mapping
from logging import getLogger
from uuid import uuid4

from typesense import Client

logger = getLogger("airbyte")


class TypesenseWriter:
    write_buffer = []

    def __init__(self, client: Client, steam_name: str, batch_size: int = 1000):
        self.client = client
        self.steam_name = steam_name
        self.batch_size = batch_size

    def queue_write_operation(self, data: Mapping):
        random_key = str(uuid4())
        data_with_id = data if "id" in data else {**data, "id": random_key}
        self.write_buffer.append(data_with_id)
        if len(self.write_buffer) == self.batch_size:
            self.flush()

    def flush(self):
        buffer_size = len(self.write_buffer)
        if buffer_size == 0:
            return
        logger.info(f"flushing {buffer_size} records")
        self.client.collections[self.steam_name].documents.import_(self.write_buffer)
        self.write_buffer.clear()
