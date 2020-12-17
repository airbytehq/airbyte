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

import requests
from airbyte_protocol import AirbyteCatalog, AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteCatalog, Type
from base_python import AirbyteLogger, BaseSource

from .client import Client


class SourceMicrosoftTeams(BaseSource):
    client_class = Client

    def __init__(self):
        super().__init__()

    def _get_client(self, config: json):
        """Construct client"""
        client = self.client_class(config=config)
        return client

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        client = self._get_client(config)
        return AirbyteCatalog(streams=client.get_streams())

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        client = self._get_client(config)

        logger.info(f"Starting syncing {self.__class__.__name__}")
        for configured_stream in catalog.streams:
            stream = configured_stream.stream
            if stream.name not in client.ENTITY_MAP.keys():
                continue
            try:
                for record in self._read_record(client=client, stream=stream.name):
                    yield AirbyteMessage(type=Type.RECORD, record=record)
            except requests.exceptions.RequestException:
                logger.error(f"Get {stream.name} error")
        logger.info(f"Finished syncing {self.__class__.__name__}")

    def _read_record(self, client: Client, stream: str):
        for record in client.ENTITY_MAP[stream]():
            for item in record:
                now = int(datetime.now().timestamp()) * 1000
                yield AirbyteRecordMessage(stream=stream, data=item, emitted_at=now)
