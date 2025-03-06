# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from functools import lru_cache
from typing import Any, Callable, Generic, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Type, TypeVar, Union

from source_faker.canon.canonical_model import CanonicalModel

from airbyte_cdk import (
    AirbyteMessage,
    AirbyteStream,
    ConfiguredAirbyteStream,
    ConnectorStateManager,
    Cursor,
    InternalConfig,
    Record,
    Stream,
    StreamFacade,
    SyncMode,
)
from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteStream,
    ConfiguredAirbyteStream,
    Level,
    SyncMode,
)
from airbyte_cdk.models import (
    Type as MessageType,
)
from airbyte_cdk.sources import AbstractSource, Source
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.abstract_stream_facade import AbstractStreamFacade
from airbyte_cdk.sources.streams.concurrent.availability_strategy import StreamAvailability
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.types import Record
from airbyte_cdk.sources.utils.slice_logger import SliceLogger


T = TypeVar("T", bound=CanonicalModel)


# This is also a callable...
class TransformFunction(Generic[T], ABC):
    @abstractmethod
    def __call__(self, record: Record) -> Record:
        pass


class CanonicalPartition(Partition):
    def __init__(self, canonical_model_type: Type[T], transform_function: TransformFunction[T], partition: Partition):
        self._canonical_model_type = canonical_model_type
        self._transform_function = transform_function
        self._partition = partition

    def read(self) -> Iterable[Record]:
        for record in self._partition.read():
            canonical_record = self._transform_function(record)
            self._canonical_model_type.validate(canonical_record.data)
            self._datetime_to_string(canonical_record.data)
            yield canonical_record

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return self._partition.to_slice()

    def stream_name(self) -> str:
        return self._canonical_model_type.stream_name()

    def cursor_field(self) -> Optional[str]:
        return "updated_at"

    def __hash__(self) -> int:
        return hash(self._partition)

    def _datetime_to_string(self, data: Any) -> Any:
        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = self._datetime_to_string(value)
        elif isinstance(data, list):
            for item in data:
                item = self._datetime_to_string(item)
        elif isinstance(data, datetime):
            return data.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return data


class CanonicalStream(AbstractStream):
    def __init__(
        self,
        stream: AbstractStream,
        canonical_model_type: Type[T],
        transform_function: TransformFunction[T],
        cursor_override: Optional[Cursor] = None,
        namespace: Optional[str] = None,
        logger: logging.Logger = logging.getLogger("airbyte"),
    ):
        self._stream = stream
        self._canonical_model_type = canonical_model_type
        self._transform_function = transform_function
        self._namespace = namespace
        self._logger = logger
        self._cursor = cursor_override

    def generate_partitions(self) -> Iterable[Partition]:
        for partition in self._stream.generate_partitions():
            yield CanonicalPartition(self._canonical_model_type, self._transform_function, partition)

    @property
    def cursor(self) -> Cursor:
        if self._cursor is not None:
            return self._cursor
        else:
            return self._stream.cursor

    @property
    def name(self) -> str:
        return self._canonical_model_type.stream_name()

    @property
    def cursor_field(self) -> Optional[str]:
        return "updated_at"

    def check_availability(self) -> StreamAvailability:
        return self._stream.check_availability()

    def get_json_schema(self) -> Mapping[str, Any]:
        return self._canonical_model_type.model_json_schema()

    def as_airbyte_stream(self) -> AirbyteStream:
        stream = AirbyteStream(
            name=self.name,
            json_schema=dict(self._canonical_model_type.model_json_schema()),
            supported_sync_modes=[SyncMode.full_refresh],
            is_resumable=False,
        )

        if self._namespace:
            stream.namespace = self._namespace

        if self.cursor_field:
            stream.source_defined_cursor = True
            stream.is_resumable = True
            stream.supported_sync_modes.append(SyncMode.incremental)
            stream.default_cursor_field = [self.cursor_field]

        keys = ["id"]
        if keys and len(keys) > 0:
            stream.source_defined_primary_key = [[key] for key in keys]

        return stream

    def log_stream_sync_configuration(self) -> None:
        self._logger.debug(
            f"Syncing stream instance: {self.name}",
            extra={
                "primary_key": ["id"],
                "cursor_field": self.cursor_field,
            },
        )


def create_canonical_stream(
    stream: AbstractStream,
    canonical_model_type: Type[T],
    transform_function: TransformFunction[T],
    cursor_override: Optional[Cursor],
    namespace: Optional[str] = None,
) -> CanonicalStream:
    return CanonicalStream(stream, canonical_model_type, transform_function, cursor_override, namespace)


class CanonicalStreamFacade(AbstractStreamFacade[CanonicalStream], Stream):
    def __init__(
        self,
        stream: CanonicalStream,
        cursor: Cursor,
        slice_logger: SliceLogger,
        logger: logging.Logger,
    ):
        self._stream = stream
        self._cursor = cursor
        self._slice_logger = slice_logger
        self._logger = logger

    @property
    def state(self) -> MutableMapping[str, Any]:
        raise NotImplementedError("This should not be called as part of the Concurrent CDK code. Please report the problem to Airbyte")

    @state.setter
    def state(self, value: Mapping[str, Any]) -> None:
        pass

    def read(
        self,
        configured_stream: ConfiguredAirbyteStream,
        logger: logging.Logger,
        slice_logger: SliceLogger,
        stream_state: MutableMapping[str, Any],
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ) -> Iterable[StreamData]:
        yield from self._read_records()

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        try:
            yield from self._read_records()
        except Exception as exc:
            if hasattr(self._cursor, "state"):
                state = str(self._cursor.state)
            else:
                # This shouldn't happen if the ConcurrentCursor was used
                state = "unknown; no state attribute was available on the cursor"
            yield AirbyteMessage(
                type=MessageType.LOG,
                log=AirbyteLogMessage(level=Level.ERROR, message=f"Cursor State at time of exception: {state}"),
            )
            raise exc

    def _read_records(self) -> Iterable[StreamData]:
        for partition in self._stream.generate_partitions():
            if self._slice_logger.should_log_slice_message(self._logger):
                yield self._slice_logger.create_slice_log_message(partition.to_slice())
            for record in partition.read():
                yield record.data

    @property
    def name(self) -> str:
        return self._stream.name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        # This method is not expected to be called directly. It is only implemented for backward compatibility with the old interface
        return self.as_airbyte_stream().source_defined_primary_key  # type: ignore # source_defined_primary_key is known to be an Optional[List[List[str]]]

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        if self._stream.cursor_field is None:
            return []
        else:
            return self._stream.cursor_field

    @property
    def cursor(self) -> Optional[Cursor]:  # type: ignore[override] # StreamFaced expects to use only airbyte_cdk.sources.streams.concurrent.cursor.Cursor
        return self._cursor

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        return {}  # FIXME

    @property
    def supports_incremental(self) -> bool:
        return True  # FIXME

    def check_availability(self, logger: logging.Logger, source: Optional["Source"] = None) -> Tuple[bool, Optional[str]]:
        """
        Verifies the stream is available. Delegates to the underlying AbstractStream and ignores the parameters
        :param logger: (ignored)
        :param source:  (ignored)
        :return:
        """
        availability = self._stream.check_availability()
        return availability.is_available(), availability.message()

    def as_airbyte_stream(self) -> AirbyteStream:
        return self._stream.as_airbyte_stream()

    def log_stream_sync_configuration(self) -> None:
        self._stream.log_stream_sync_configuration()

    def get_underlying_stream(self) -> CanonicalStream:
        return self._stream


def create_canonical_stream_facade(
    stream: AbstractStream,
    canonical_model_type: Type[T],
    transform_function: TransformFunction[T],
    cursor_override: Optional[Cursor],
    logger: logging.Logger,
    slice_logger: SliceLogger,
    namespace: Optional[str] = None,
) -> CanonicalStreamFacade:
    canonical_stream = create_canonical_stream(stream, canonical_model_type, transform_function, cursor_override, namespace)
    return CanonicalStreamFacade(canonical_stream, canonical_stream.cursor, slice_logger, logger)
