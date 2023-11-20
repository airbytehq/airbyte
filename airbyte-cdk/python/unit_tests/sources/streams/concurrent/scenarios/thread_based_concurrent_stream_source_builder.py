#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConnectorSpecification, DestinationSyncMode, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.availability_strategy import AbstractAvailabilityStrategy, StreamAvailability, StreamAvailable
from airbyte_cdk.sources.streams.concurrent.cursor import NoopCursor
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.thread_based_concurrent_stream import ThreadBasedConcurrentStream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_protocol.models import ConfiguredAirbyteStream
from unit_tests.sources.file_based.scenarios.scenario_builder import SourceBuilder


class LegacyStream(Stream):
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return None

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        yield from []


class ConcurrentCdkSource(AbstractSource):
    def __init__(self, streams: List[ThreadBasedConcurrentStream], message_repository: Optional[MessageRepository]):
        self._streams = streams
        self._message_repository = message_repository

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        # Check is not verified because it is up to the source to implement this method
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [StreamFacade(s, LegacyStream(), NoopCursor()) for s in self._streams]

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(connectionSpecification={})

    def read_catalog(self, catalog_path: str) -> ConfiguredAirbyteCatalog:
        return ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=StreamFacade(s, LegacyStream(), NoopCursor()).as_airbyte_stream(),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
                for s in self._streams
            ]
        )

    @property
    def message_repository(self) -> Union[None, MessageRepository]:
        return self._message_repository


class InMemoryPartitionGenerator(PartitionGenerator):
    def __init__(self, partitions: List[Partition]):
        self._partitions = partitions

    def generate(self) -> Iterable[Partition]:
        yield from self._partitions


class InMemoryPartition(Partition):
    def __init__(self, name, _slice, records):
        self._name = name
        self._slice = _slice
        self._records = records

    def read(self) -> Iterable[Record]:
        for record_or_exception in self._records:
            if isinstance(record_or_exception, Exception):
                raise record_or_exception
            else:
                yield record_or_exception

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return self._slice

    def __hash__(self) -> int:
        if self._slice:
            # Convert the slice to a string so that it can be hashed
            s = json.dumps(self._slice, sort_keys=True)
            return hash((self._name, s))
        else:
            return hash(self._name)


class ConcurrentSourceBuilder(SourceBuilder[ConcurrentCdkSource]):
    def __init__(self):
        self._streams: List[ThreadBasedConcurrentStream] = []
        self._message_repository = None

    def build(self, configured_catalog: Optional[Mapping[str, Any]]) -> ConcurrentCdkSource:
        for stream in self._streams:
            if not stream._message_repository:
                stream._message_repository = self._message_repository
        return ConcurrentCdkSource(self._streams, self._message_repository)

    def set_streams(self, streams: List[ThreadBasedConcurrentStream]) -> "ConcurrentSourceBuilder":
        self._streams = streams
        return self

    def set_message_repository(self, message_repository: MessageRepository) -> "ConcurrentSourceBuilder":
        self._message_repository = message_repository
        return self


class AlwaysAvailableAvailabilityStrategy(AbstractAvailabilityStrategy):
    def check_availability(self, logger: logging.Logger) -> StreamAvailability:
        return StreamAvailable()


class NeverLogSliceLogger(SliceLogger):
    def should_log_slice_message(self, logger: logging.Logger) -> bool:
        return False
