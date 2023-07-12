from typing import Mapping
from logging import getLogger

from destination_planhat_analytics.client import PlanHatClient

logger = getLogger("airbyte")


class PlanHatWriter:
    write_buffer = []

    def __init__(self, client: PlanHatClient):
        self.client = client

    def queue_write_operation(self, record: Mapping):
        self.write_buffer.append(record)
        if len(self.write_buffer) == self.client.batch_size:
            self.flush()

    def flush(self):
        response = self.client.write(self.write_buffer)
        if self.client.api_token:
            if response.json()["errors"] != []:
                logger.warning(response.json())
            else:
                logger.info(response.json())
        self.write_buffer.clear()
