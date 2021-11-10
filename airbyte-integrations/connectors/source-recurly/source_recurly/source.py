#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


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
