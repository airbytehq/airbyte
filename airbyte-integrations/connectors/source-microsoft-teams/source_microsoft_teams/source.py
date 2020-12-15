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

from datetime import datetime
from typing import Generator
from msal.exceptions import MsalServiceError

from .client import Client

from airbyte_protocol import AirbyteCatalog, AirbyteConnectionStatus, \
    AirbyteMessage, Status, ConfiguredAirbyteCatalog, Type, AirbyteRecordMessage
from base_python import AirbyteLogger, ConfigContainer, Source


class SourceMicrosoftTeams(Source):
    client_class = Client

    def __init__(self):
        super().__init__()

    def _get_client(self, config_container: ConfigContainer):
        """Construct client"""
        config = config_container.rendered_config
        client = self.client_class(config=config)
        return client

    def check(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteConnectionStatus:
        client = self._get_client(config_container)
        alive, error = client.health_check()
        if not alive:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f'{error}')
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteCatalog:
        client = self._get_client(config_container)
        return AirbyteCatalog(streams=client.get_streams())

    def read(
        self, logger: AirbyteLogger, config_container: ConfigContainer, catalog_path: str, state: str = None
    ) -> Generator[AirbyteMessage, None, None]:
        config = self.read_config(catalog_path)
        catalog = ConfiguredAirbyteCatalog.parse_obj(config)

        client = self._get_client(config_container)

        logger.info(f"Starting syncing {self.__class__.__name__}")
        for configured_stream in catalog.streams:
            stream = configured_stream.stream
            if stream.name not in client.ENTITY_MAP.keys():
                continue
            for record in self._read_record(client=client, stream=stream.name):
                yield AirbyteMessage(type=Type.RECORD, record=record)
        logger.info(f"Finished syncing {self.__class__.__name__}")

    def _read_record(self, client: Client, stream: str):
        for record in client.ENTITY_MAP[stream]():
            now = int(datetime.now().timestamp()) * 1000
            yield AirbyteRecordMessage(stream=stream, data=record, emitted_at=now)
