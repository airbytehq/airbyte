#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import uuid
from collections import Mapping
from meilisearch import Client


class MeiliWriter:
    write_buffer = []
    flush_interval = 10000

    def __init__(self, client: Client, steam_name: str, primary_key: str):
        self.client = client
        self.steam_name = steam_name
        self.primary_key = primary_key

    def queue_write_operation(self, data: Mapping):
        random_key = str(uuid.uuid4())
        self.write_buffer.append({**data, self.primary_key: random_key })
        if len(self.write_buffer) == self.flush_interval:
            self.flush()

    def flush(self):
        if len(self.write_buffer) == 0:
            return

        response = self.client.index(self.steam_name).add_documents(self.write_buffer)
        while True:
            task = self.client.get_task(response.task_uid)
            status = task["status"]
            if status == "succeeded" or status == "failed":
                break

        self.write_buffer.clear()
