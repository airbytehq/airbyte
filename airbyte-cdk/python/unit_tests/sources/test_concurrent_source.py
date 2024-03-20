#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent
import logging
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple
from unittest.mock import Mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.availability_strategy import StreamAvailability, StreamAvailable, StreamUnavailable
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor, FinalStateCursor
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_protocol.models import AirbyteStream

logger = logging.getLogger("airbyte")


class _MockSource(ConcurrentSource):
    def __init__(
        self,
        check_lambda: Callable[[], Tuple[bool, Optional[Any]]] = None,
        per_stream: bool = True,
        message_repository: MessageRepository = InMemoryMessageRepository(),
        threadpool: ThreadPoolManager = ThreadPoolManager(
            concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="workerpool"), logger
        ),
        exception_on_missing_stream: bool = True,
    ):
        super().__init__(threadpool, Mock(), Mock(), message_repository)
        self.check_lambda = check_lambda
        self.per_stream = per_stream
        self.exception_on_missing_stream = exception_on_missing_stream
        self._message_repository = message_repository


MESSAGE_FROM_REPOSITORY = Mock()


class _MockStream(AbstractStream):
    def __init__(self, name: str, message_repository: MessageRepository, available: bool = True, json_schema: Dict[str, Any] = {}):
        self._name = name
        self._available = available
        self._json_schema = json_schema
        self._message_repository = message_repository

    def generate_partitions(self) -> Iterable[Partition]:
        yield _MockPartition(self._name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def cursor_field(self) -> Optional[str]:
        raise NotImplementedError

    def check_availability(self) -> StreamAvailability:
        if self._available:
            return StreamAvailable()
        else:
            return StreamUnavailable("stream is unavailable")

    def get_json_schema(self) -> Mapping[str, Any]:
        return self._json_schema

    def as_airbyte_stream(self) -> AirbyteStream:
        return AirbyteStream(name=self.name, json_schema=self.get_json_schema(), supported_sync_modes=[SyncMode.full_refresh])

    def log_stream_sync_configuration(self) -> None:
        raise NotImplementedError

    @property
    def cursor(self) -> Cursor:
        return FinalStateCursor(stream_name=self._name, stream_namespace=None, message_repository=self._message_repository)


class _MockPartition(Partition):
    def __init__(self, name: str):
        self._name = name
        self._closed = False

    def read(self) -> Iterable[Record]:
        yield from [Record({"key": "value"}, self._name)]

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return {}

    def stream_name(self) -> str:
        return self._name

    def close(self) -> None:
        self._closed = True

    def is_closed(self) -> bool:
        return self._closed

    def __hash__(self) -> int:
        return hash(self._name)


def test_concurrent_source_reading_from_no_streams():
    message_repository = InMemoryMessageRepository()
    stream = _MockStream("my_stream", message_repository,False, {})
    source = _MockSource(message_repository=message_repository)
    messages = []
    for m in source.read([stream]):
        messages.append(m)
