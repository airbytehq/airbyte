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
from typing import DefaultDict, Dict, Generator

from airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Status,
    SyncMode,
)
from base_python import AirbyteLogger, Source

from .client import Client


class SourceMailchimp(Source):
    """
    Mailchimp API Reference: https://mailchimp.com/developer/api/
    """

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        client = self._client(config)
        alive, error = client.health_check()
        if not alive:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{error.title}: {error.detail}")

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        client = self._client(config)

        return AirbyteCatalog(streams=client.get_streams())

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        client = self._client(config)

        logger.info("Starting syncing mailchimp")
        for configured_stream in catalog.streams:
            yield from self._read_record(client=client, configured_stream=configured_stream, state=state)

        logger.info("Finished syncing mailchimp")

    def _client(self, config: json):
        client = Client(username=config["username"], apikey=config["apikey"])

        return client

    @staticmethod
    def _read_record(
        client: Client, configured_stream: ConfiguredAirbyteStream, state: DefaultDict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        entity_map = {
            "Lists": client.lists,
            "Campaigns": client.campaigns,
        }

        stream_name = configured_stream.stream.name

        if configured_stream.sync_mode == SyncMode.full_refresh:
            state.pop(stream_name, None)

        for record in entity_map[stream_name](state=state):
            yield record
