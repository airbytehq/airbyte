#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from logging import Logger
from typing import Any, Callable, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.models import AirbyteStream, SyncMode
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.availability_strategy import StreamAvailability
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


class DefaultStream(AbstractStream):
    def __init__(
        self,
        partition_generator: PartitionGenerator,
        name: str,
        json_schema: Union[Mapping[str, Any], Callable[[], Mapping[str, Any]]],
        primary_key: List[str],
        cursor_field: Optional[str],
        logger: Logger,
        cursor: Cursor,
        namespace: Optional[str] = None,
        supports_file_transfer: bool = False,
    ) -> None:
        self._stream_partition_generator = partition_generator
        self._name = name
        self._json_schema = json_schema
        self._primary_key = primary_key
        self._cursor_field = cursor_field
        self._logger = logger
        self._cursor = cursor
        self._namespace = namespace
        self._supports_file_transfer = supports_file_transfer

    def generate_partitions(self) -> Iterable[Partition]:
        yield from self._stream_partition_generator.generate()

    @property
    def name(self) -> str:
        return self._name

    @property
    def namespace(self) -> Optional[str]:
        return self._namespace

    @property
    def cursor_field(self) -> Optional[str]:
        return self._cursor_field

    def get_json_schema(self) -> Mapping[str, Any]:
        return self._json_schema() if callable(self._json_schema) else self._json_schema

    def as_airbyte_stream(self) -> AirbyteStream:
        stream = AirbyteStream(
            name=self.name,
            json_schema=dict(self.get_json_schema()),
            supported_sync_modes=[SyncMode.full_refresh],
            is_resumable=False,
            is_file_based=self._supports_file_transfer,
        )

        if self._namespace:
            stream.namespace = self._namespace

        if self._cursor_field:
            stream.source_defined_cursor = True
            stream.is_resumable = True
            stream.supported_sync_modes.append(SyncMode.incremental)
            stream.default_cursor_field = [self._cursor_field]

        keys = self._primary_key
        if keys and len(keys) > 0:
            stream.source_defined_primary_key = [[key] for key in keys]

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

    def check_availability(self) -> StreamAvailability:
        """
        Check stream availability by attempting to read the first record of the stream.
        """
        try:
            partition = next(iter(self.generate_partitions()))
        except StopIteration:
            # NOTE: The following comment was copied from legacy stuff and I don't know how relevant it is:
            # If stream_slices has no `next()` item (Note - this is different from stream_slices returning [None]!)
            # This can happen when a substream's `stream_slices` method does a `for record in parent_records: yield <something>`
            # without accounting for the case in which the parent stream is empty.
            return StreamAvailability.unavailable(
                f"Cannot attempt to connect to stream {self.name} - no stream slices were found"
            )
        except AirbyteTracedException as error:
            return StreamAvailability.unavailable(
                error.message or error.internal_message or "<no error message>"
            )

        try:
            next(iter(partition.read()))
            return StreamAvailability.available()
        except StopIteration:
            self._logger.info(f"Successfully connected to stream {self.name}, but got 0 records.")
            return StreamAvailability.available()
        except AirbyteTracedException as error:
            return StreamAvailability.unavailable(
                error.message or error.internal_message or "<no error message>"
            )
