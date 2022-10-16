#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import time
from collections.abc import Mapping
from uuid import uuid4

from meilisearch import Client


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
        if len(self.write_buffer) == 0:
            return

        response = self.client.index(self.steam_name).add_documents(self.write_buffer)
        self.wait_for_job(response.task_uid)
        self.write_buffer.clear()

    def wait_for_job(self, task_uid: str):
        while True:
            time.sleep(1)
            task = self.client.get_task(task_uid)
            status = task["status"]
            if status == "succeeded" or status == "failed":
                break
