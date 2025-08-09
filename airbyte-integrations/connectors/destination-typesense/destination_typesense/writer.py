#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from collections import defaultdict
from collections.abc import Mapping
from logging import getLogger
from uuid import uuid4

from typesense import Client


logger = getLogger("airbyte")


class TypesenseWriter:
    write_buffer: list[tuple[str, Mapping]] = []

    def __init__(self, client: Client, batch_size: int = 10000):
        self.client = client
        self.batch_size = batch_size or 10000

    def queue_write_operation(self, stream_name: str, data: Mapping):
        random_key = str(uuid4())
        self.write_buffer.append(
            (
                stream_name,
                {
                    "id": random_key,
                    **data,
                },
            )
        )
        if len(self.write_buffer) == self.batch_size:
            self.flush()

    def flush(self):
        buffer_size = len(self.write_buffer)
        if buffer_size == 0:
            return
        logger.info(f"flushing {buffer_size} records")

        grouped_by_stream: defaultdict[str, list[Mapping]] = defaultdict(list)
        for stream, data in self.write_buffer:
            grouped_by_stream[stream].append(data)

        for stream, data in grouped_by_stream.items():
            self.client.collections[stream].documents.import_(data)
        self.write_buffer.clear()
