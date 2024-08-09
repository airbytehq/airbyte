import json
import logging
from typing import Iterable, Optional, Mapping, Any, List, Union

from airbyte_cdk import MessageRepository, TState, StreamSlice, FinalStateCursor, ConcurrentSource, YamlDeclarativeSource
from airbyte_cdk.connector import TConfig
from airbyte_cdk.models import AirbyteCatalog, AirbyteConnectionStatus, AirbyteMessage, Type
from airbyte_cdk.sources.declarative.retrievers import Retriever
from airbyte_cdk.sources.declarative.stream_slicers import StreamSlicer
from airbyte_cdk.sources.source import TCatalog
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.availability_strategy import AbstractAvailabilityStrategy, StreamAvailability, StreamAvailable
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger


class AlwaysAvailableAvailabilityStrategy(AbstractAvailabilityStrategy):
    """
    Copy paste of something in the unit tests because we probably don't care about the availability strategy as it is getting removed from
    the non concurrent part of the code (see https://github.com/airbytehq/airbyte/pull/40682)
    """
    def check_availability(self, logger: logging.Logger) -> StreamAvailability:
        return StreamAvailable()


class DeclarativeConcurrentSource(YamlDeclarativeSource):  # our entrypoint requires a Source

    def _streams(self, config) -> List[AbstractStream]:
        streams = []
        for stream in self.streams(config):
            json_schema = stream.get_json_schema()
            # FIXME This is a bit annoying because we it'll not work with all the stream slicers. The issue is that the stream slicing part
            #  is not exposed anywhere except through `stream_slices`. This means that we either:
            #  * have the DeclarativePartitionGenerator relying on the stream instead of the stream slicer (but we would have to keep more legacy code)
            #  * find a way to access/expose a stream slicer concept through the manifest
            #  For this PoC, we will just assume the retriever expose a stream_slicer
            stream_slicer = stream.retriever.stream_slicer
            streams.append(
                DefaultStream(
                    DeclarativePartitionGenerator(stream_slicer, stream.retriever, self._message_repository, stream.name, json_schema),
                    stream.name,
                    json_schema,
                    AlwaysAvailableAvailabilityStrategy(),  # should we remove this concept
                    self._to_clean_primary_key(stream.primary_key),
                    self._to_clean_cursor_field(stream.cursor_field),
                    self.logger,
                    FinalStateCursor(stream.name, stream.namespace, self._message_repository),  # FIXME change this to support incremental or RFR streams
                    stream.namespace,
                )
            )
        return streams

    def read(self, logger: logging.Logger, config: TConfig, catalog: TCatalog, state: Optional[TState] = None) -> Iterable[AirbyteMessage]:
        concurrency_level = 10
        catalog_streams = set(map(lambda stream: stream.stream.name, catalog.streams))
        enable_streams = [stream for stream in self._streams(config) if stream.name in catalog_streams]
        yield from ConcurrentSource.create(concurrency_level, concurrency_level // 2, logger, DebugSliceLogger(), self._message_repository).read(enable_streams)

    def discover(self, logger: logging.Logger, config: TConfig) -> AirbyteCatalog:
        # TODO implement
        pass

    def check(self, logger: logging.Logger, config: TConfig) -> AirbyteConnectionStatus:
        # TODO implement
        pass

    @staticmethod
    def _to_clean_primary_key(primary_key: Optional[Union[str, List[str], List[List[str]]]]) -> List[str]:
        if not primary_key:
            return []
        elif isinstance(primary_key, str):
            return [primary_key]
        elif isinstance(primary_key, List):
            first_element = primary_key[0]
            if isinstance(first_element, str):
                return primary_key
            else:
                raise ValueError("Composite primary keys are not supported")
        raise ValueError(f"Invalid primary key type {type(primary_key)}")

    @staticmethod
    def _to_clean_cursor_field(cursor_field: Union[str, List[str]]) -> Optional[str]:
        if not cursor_field:
            return None
        elif isinstance(cursor_field, List) and len(cursor_field) == 1:
            return cursor_field[0]
        raise ValueError(f"Invalid cursor field `{cursor_field}`: only str is supported")


class DeclarativePartition(Partition):
    def __init__(self, retriever: Retriever, message_repository: MessageRepository, stream_name: str, stream_slice: StreamSlice, json_schema: Mapping[str, Any]):
        self._retriever = retriever
        self._stream_name = stream_name
        self._message_repository = message_repository
        self._json_schema = json_schema
        self._stream_slice = stream_slice

        self._is_closed = False

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return self._stream_slice

    def stream_name(self) -> str:
        return self._stream_name

    def read(self) -> Iterable[Record]:
        for stream_data in self._retriever.read_records(self._json_schema, self._stream_slice):
            if isinstance(stream_data, AirbyteMessage):
                if stream_data.type == Type.RECORD:
                    yield Record(stream_data.record.data, stream_data.record.stream)
                else:
                    self._message_repository.emit_message(stream_data)
            else:
                yield Record(stream_data, self._stream_name)

    def close(self) -> None:
        # FIXME duplicate of StreamPartition
        # self._cursor.close_partition(self) TODO to support incremental declarative stream
        self._is_closed = True

    def is_closed(self) -> bool:
        # FIXME duplicate of StreamPartition
        return self._is_closed

    def __repr__(self) -> str:
        # FIXME duplicate of StreamPartition
        return f"StreamPartition({self._stream_name}, {self._stream_slice})"

    def __hash__(self) -> int:
        stream_slice_as_dict = dict(self._stream_slice) if self._stream_slice else None
        if stream_slice_as_dict:
            # Convert the slice to a string so that it can be hashed
            s = json.dumps(stream_slice_as_dict, sort_keys=True)
            return hash((self._stream_name, s))
        else:
            return hash(self._stream_name)


class DeclarativePartitionGenerator(PartitionGenerator):
    def __init__(self, stream_slicer: StreamSlicer, retriever: Retriever, message_repository: MessageRepository, stream_name: str, json_schema: Mapping[str, Any]):
        self._stream_slicer = stream_slicer
        self._retriever = retriever
        self._stream_name = stream_name
        self._message_repository = message_repository
        self._json_schema = json_schema

    def generate(self) -> Iterable[Partition]:
        for stream_slice in self._stream_slicer.stream_slices():
            yield DeclarativePartition(self._retriever, self._message_repository, self._stream_name, stream_slice, self._json_schema)
