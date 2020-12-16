"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from datetime import datetime
from typing import Dict, Generator

from airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from base_python import AirbyteLogger, Source

from .client import Client


class SourceRecurly(Source):
    """
    Recurly API Reference: https://developers.recurly.com/api/v2019-10-10/index.html
    """

    def __init__(self):
        super().__init__()

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        client = self._client(config)
        alive, error = client.health_check()
        if not alive:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{error}")

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        client = self._client(config)

        return AirbyteCatalog(streams=client.get_streams())

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        client = self._client(config)

        logger.info("Starting syncing recurly")
        for configured_stream in catalog.streams:
            # TODO handle incremental syncs
            stream = configured_stream.stream
            if stream.name not in client.ENTITIES:
                logger.warn(f"Stream '{stream}' not found in the recognized entities")
                continue
            for record in self._read_record(client=client, stream=stream.name):
                yield AirbyteMessage(type=Type.RECORD, record=record)

        logger.info("Finished syncing recurly")

    def _client(self, config: json):
        client = Client(api_key=config["api_key"])

        return client

    @staticmethod
    def _read_record(client: Client, stream: str):
        for record in client.get_entities(stream):
            now = int(datetime.now().timestamp()) * 1000
            yield AirbyteRecordMessage(stream=stream, data=record, emitted_at=now)
