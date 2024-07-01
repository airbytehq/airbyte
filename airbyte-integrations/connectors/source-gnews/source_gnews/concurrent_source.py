"""
To run, simply pass the api_token like `python concurrent_source.py <api_token>`
"""

import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, Mapping, Optional

import requests
from airbyte_protocol.models import AirbyteStream, SyncMode, Level

from airbyte_cdk.logger import AirbyteLogFormatter
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.availability_strategy import StreamAvailability, StreamAvailable
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor, ConcurrentCursor, CursorField
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import DateTimeStreamStateConverter
from airbyte_cdk.sources.utils.slice_logger import AlwaysLogSliceLogger

logger = logging.getLogger("airbyte")

_SEARCH_STREAM_NAME = "search"
_SEARCH_JSON_SCHEMA = {}  # TODO
_SEARCH_CURSOR_FIELD = "publishedAt"

_SEARCH_AIRBYTE_STREAM = AirbyteStream(
    name=_SEARCH_STREAM_NAME,
    json_schema=_SEARCH_JSON_SCHEMA,
    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
    source_defined_primary_key=[["url"]],
    source_defined_cursor=True,
    default_cursor_field=[_SEARCH_CURSOR_FIELD]
)


class SearchPartition(Partition):
    def __init__(self, cursor: Cursor, _slice: Dict[str, str]):
        self._cursor = cursor
        self._slice = _slice

    def read(self) -> Iterable[Record]:
        # HTTP requester would have been nice here
        response = requests.get(f"https://gnews.io/api/v4/top-headlines?token={sys.argv[1]}&from={self._slice['start']}&to={self._slice['end']}&topic=technology")
        response.raise_for_status()
        # There might be pagination and stuff but for the purpose of this test, we don't care
        yield from [Record(article, self.stream_name()) for article in response.json()["articles"]]

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return self._slice

    def stream_name(self) -> str:
        return _SEARCH_STREAM_NAME

    def close(self) -> None:
        self._cursor.close_partition(self)

    def __hash__(self) -> int:
        s = json.dumps(self._slice, sort_keys=True)
        return hash((self.stream_name, s))

    def is_closed(self) -> bool:
        return False  # FIXME I don't think this is used


class SearchStream(AbstractStream):
    def __init__(self, cursor: ConcurrentCursor, cursor_field: str):
        self._cursor = cursor
        self._cursor_field = cursor_field

    def generate_partitions(self) -> Iterable[Partition]:
        for slice_start, slice_end in self._cursor.generate_slices():
            yield SearchPartition(
                self._cursor,
                {
                    "start": slice_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "end": slice_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            )

    @property
    def name(self) -> str:
        return _SEARCH_STREAM_NAME

    @property
    def cursor_field(self) -> Optional[str]:
        return _SEARCH_CURSOR_FIELD

    def check_availability(self) -> StreamAvailability:
        # Availability strategy will be removed soon. Here, we can assume this will always be available
        return StreamAvailable()

    def get_json_schema(self) -> Mapping[str, Any]:
        return _SEARCH_JSON_SCHEMA

    def as_airbyte_stream(self) -> AirbyteStream:
        return _SEARCH_AIRBYTE_STREAM

    def log_stream_sync_configuration(self) -> None:
        pass

    @property
    def cursor(self) -> Cursor:
        return self._cursor


class GenericDateTimeStreamStateConverter(DateTimeStreamStateConverter):

    _STATE_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
    _GRANULARITY = timedelta(microseconds=1)
    _zero_value = ""  # FIXME this should be removed

    def __init__(self, record_cursor_datetime_format):
        super().__init__(is_sequential_state=False)
        self._record_cursor_datetime_format = record_cursor_datetime_format

    @property
    def zero_value(self) -> datetime:
        return datetime.min

    def increment(self, timestamp: datetime) -> datetime:
        return timestamp + self._GRANULARITY

    def output_format(self, timestamp: datetime) -> Any:
        return timestamp.strftime(self._STATE_DATETIME_FORMAT)

    def parse_timestamp(self, timestamp: str) -> datetime:
        return datetime.strptime(timestamp, self._record_cursor_datetime_format).replace(tzinfo=timezone.utc)


_NO_NAMESPACE = None
_NO_STATE = {}
_START_DATETIME = datetime.now(tz=timezone.utc) - timedelta(days=30)
_END_PROVIDER = lambda: datetime.now(tz=timezone.utc)
_LOOKBACK_WINDOW = timedelta(0)
_SLICE_RANGE = timedelta(days=7)

message_repository = InMemoryMessageRepository(Level(AirbyteLogFormatter.level_mapping[logger.level]))
concurrency_level = 2
concurrent_source = ConcurrentSource.create(concurrency_level, concurrency_level // 2, logger, AlwaysLogSliceLogger(), message_repository)
state = _NO_STATE
search_stream = SearchStream(
    ConcurrentCursor(
        _SEARCH_STREAM_NAME,
        _NO_NAMESPACE,
        state,
        message_repository,
        ConnectorStateManager(stream_instance_map={_SEARCH_STREAM_NAME: _SEARCH_AIRBYTE_STREAM}, state=state),
        GenericDateTimeStreamStateConverter("%Y-%m-%dT%H:%M:%SZ"),
        CursorField(_SEARCH_CURSOR_FIELD),
        ("start", "end"),
        _START_DATETIME,
        _END_PROVIDER,
        _LOOKBACK_WINDOW,
        _SLICE_RANGE,
    ),
    "publishedAt"
)

# FIXME what do we need to interface with the entrypoint?
for message in concurrent_source.read([search_stream]):
    print(message.json(exclude_unset=True))
