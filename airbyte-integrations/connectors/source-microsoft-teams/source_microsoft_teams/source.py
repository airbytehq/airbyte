#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime
from typing import Dict, Generator

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models.airbyte_protocol import AirbyteCatalog, AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteCatalog, Type
from airbyte_cdk.sources.deprecated.base_source import BaseSource

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
            logger.info(f"Syncing {stream.name} stream")
            for record in self._read_record(client=client, stream=stream.name):
                yield AirbyteMessage(type=Type.RECORD, record=record)
        logger.info(f"Finished syncing {self.__class__.__name__}")

    def _read_record(self, client: Client, stream: str):
        for record in client.ENTITY_MAP[stream]():
            for item in record:
                now = int(datetime.now().timestamp()) * 1000
                yield AirbyteRecordMessage(stream=stream, data=item, emitted_at=now)
