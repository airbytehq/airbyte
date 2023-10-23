#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConnectorSpecification, DestinationSyncMode, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_protocol.models import ConfiguredAirbyteStream
from unit_tests.sources.file_based.scenarios.scenario_builder import SourceBuilder


class StreamFacadeSource(AbstractSource):
    def __init__(self, streams: List[Stream], max_workers: int):
        self._streams = streams
        self._max_workers = max_workers

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [StreamFacade.create_from_stream(stream, self, stream.logger, self._max_workers) for stream in self._streams]

    @property
    def message_repository(self) -> Union[None, MessageRepository]:
        return InMemoryMessageRepository()

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        return ConnectorSpecification(connectionSpecification={})

    def read_catalog(self, catalog_path: str) -> ConfiguredAirbyteCatalog:
        return ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=s.as_airbyte_stream(),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
                for s in self._streams
            ]
        )


class StreamFacadeSourceBuilder(SourceBuilder[StreamFacadeSource]):
    def __init__(self):
        self._source = None
        self._streams = []
        self._max_workers = 1

    def set_streams(self, streams: List[Stream]) -> "StreamFacadeSourceBuilder":
        self._streams = streams
        return self

    def set_max_workers(self, max_workers: int):
        self._max_workers = max_workers
        return self

    def build(self, configured_catalog: Optional[Mapping[str, Any]]) -> StreamFacadeSource:
        return StreamFacadeSource(self._streams, self._max_workers)
