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

from collections import defaultdict
from typing import Generator, DefaultDict

from airbyte_protocol import AirbyteCatalog, AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status
from base_python import AirbyteLogger, ConfigContainer, Source

from .client import Client


class SourceMailchimp(Source):
    """
    Mailchimp API Reference: https://mailchimp.com/developer/api/
    """

    def __init__(self):
        super().__init__()

    def check(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteConnectionStatus:
        client = self._client(config_container)
        alive, error = client.health_check()
        if not alive:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{error.title}: {error.detail}")

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteCatalog:
        client = self._client(config_container)

        return AirbyteCatalog(streams=client.get_streams())

    def read(
        self, logger: AirbyteLogger, config_container: ConfigContainer, catalog_path, state_path: str = None
    ) -> Generator[AirbyteMessage, None, None]:
        client = self._client(config_container)

        if state_path:
            logger.info("Starting sync with provided state file")
            state_obj = json.loads(open(state_path, "r").read())
        else:
            logger.info("No state provided, starting fresh sync")
            state_obj = {}

        state = defaultdict(dict, state_obj)
        catalog = ConfiguredAirbyteCatalog.parse_obj(self.read_config(catalog_path))

        logger.info("Starting syncing mailchimp")
        for configured_stream in catalog.streams:
            stream = configured_stream.stream
            for record in self._read_record(client=client, stream=stream.name, state=state):
                yield record

        logger.info("Finished syncing mailchimp")

    def _client(self, config_container: ConfigContainer):
        config = config_container.rendered_config
        client = Client(username=config["username"], apikey=config["apikey"])

        return client

    def _read_record(self, client: Client, stream: str, state: DefaultDict[str, any] = None) -> Generator[AirbyteMessage, None, None]:
        entity_map = {
            "Lists": client.lists,
            "Campaigns": client.campaigns,
        }

        for record in entity_map[stream](state=state):
            yield record
