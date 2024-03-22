#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from functools import lru_cache
from logging import Logger
from typing import Any, Iterable, List, Mapping, Optional

from airbyte_cdk.models import AirbyteStream, SyncMode
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.availability_strategy import AbstractAvailabilityStrategy, StreamAvailability
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator


class DefaultStream(AbstractStream):
    def __init__(
        self,
        partition_generator: PartitionGenerator,
        name: str,
        json_schema: Mapping[str, Any],
        availability_strategy: AbstractAvailabilityStrategy,
        primary_key: List[str],
        cursor_field: Optional[str],
        logger: Logger,
        cursor: Cursor,
        namespace: Optional[str] = None,
    ) -> None:
        self._stream_partition_generator = partition_generator
        self._name = name
        self._json_schema = json_schema
        self._availability_strategy = availability_strategy
        self._primary_key = primary_key
        self._cursor_field = cursor_field
        self._logger = logger
        self._cursor = cursor
        self._namespace = namespace

    def generate_partitions(self) -> Iterable[Partition]:
        yield from self._stream_partition_generator.generate()

    @property
    def name(self) -> str:
        return self._name

    @property
    def namespace(self) -> Optional[str]:
        return self._namespace

    def check_availability(self) -> StreamAvailability:
        return self._availability_strategy.check_availability(self._logger)

    @property
    def cursor_field(self) -> Optional[str]:
        return self._cursor_field

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        return self._json_schema

    def as_airbyte_stream(self) -> AirbyteStream:
        stream = AirbyteStream(name=self.name, json_schema=dict(self._json_schema), supported_sync_modes=[SyncMode.full_refresh])

        if self._namespace:
            stream.namespace = self._namespace

        if self._cursor_field:
            stream.source_defined_cursor = True
            stream.supported_sync_modes.append(SyncMode.incremental)
            stream.default_cursor_field = [self._cursor_field]

        keys = self._primary_key
        if keys and len(keys) > 0:
            stream.source_defined_primary_key = [keys]

        return stream

    def log_stream_sync_configuration(self) -> None:
        self._logger.debug(
            f"Syncing stream instance: {self.name}",
            extra={
                "primary_key": self._primary_key,
                "cursor_field": self.cursor_field,
            },
        )

    @property
    def cursor(self) -> Cursor:
        return self._cursor
