import logging
from typing import Mapping, Any, List, Tuple, Optional

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
import concurrent
import logging
from typing import Any, Iterable, List, Mapping, Optional, Union
from unittest.mock import Mock

import pytest
import freezegun
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, SyncMode, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, AirbyteStream, DestinationSyncMode, AirbyteTraceMessage, TraceType, AirbyteStreamStatusTraceMessage, AirbyteStreamStatus, StreamDescriptor, AirbyteRecordMessage
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import NoopCursor
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger


# FIXME: should there be a test for a failing sync?

class _MockStream(Stream):
    def __init__(self, slice_to_records: Mapping[str, List[Mapping[str, Any]]], name: str):
        self._slice_to_records = slice_to_records
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return None

    def stream_slices(
            self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for partition in self._slice_to_records.keys():
            yield {"partition": partition}

    def read_records(
            self,
            sync_mode: SyncMode,
            cursor_field: Optional[List[str]] = None,
            stream_slice: Optional[Mapping[str, Any]] = None,
            stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        yield from self._slice_to_records[stream_slice["partition"]]

    def get_json_schema(self) -> Mapping[str, Any]:
        return {}

class _MockSource(AbstractSource):
    def __init__(self, streams):
        self._streams = streams

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        pass

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return self._streams


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_source_read_no_state_single_stream_single_partition_full_refresh():
    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    slice_to_partition = {"1": records}
    streams = [
        _MockStream(slice_to_partition, "stream")
    ]
    source = _MockSource(streams)
    logger = Mock()
    logger.level = logging.INFO
    config = {}
    state = None
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                cursor_field=None,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]

    )
    messages = list(source.read(logger, config, catalog, state))

    expected_messages = [
        AirbyteMessage(type=MessageType.TRACE,
                       trace=AirbyteTraceMessage(type=TraceType.STREAM_STATUS,
                                                 emitted_at=1577836800000.0,
                                                 error=None,
                                                 estimate=None,
                                                 stream_status=AirbyteStreamStatusTraceMessage(stream_descriptor=StreamDescriptor(name="stream"),
                                                                                               status=AirbyteStreamStatus(AirbyteStreamStatus.STARTED)))),
        AirbyteMessage(type=MessageType.LOG,
                       log=AirbyteLogMessage(level=Level.INFO, message='slice:{"partition": "1"}')),
        AirbyteMessage(type=MessageType.TRACE,
                       trace=AirbyteTraceMessage(type=TraceType.STREAM_STATUS,
                                                 emitted_at=1577836800000.0,
                                                 error=None,
                                                 estimate=None,
                                                 stream_status=AirbyteStreamStatusTraceMessage(stream_descriptor=StreamDescriptor(name="stream"),
                                                                                               status=AirbyteStreamStatus(AirbyteStreamStatus.RUNNING)))),
        AirbyteMessage(type=MessageType.RECORD,
                       record=AirbyteRecordMessage(
                            stream="stream",
                            data=records[0],
                            emitted_at=1577836800000,
                       )),
        AirbyteMessage(type=MessageType.RECORD,
                       record=AirbyteRecordMessage(
                           stream="stream",
                           data=records[1],
                           emitted_at=1577836800000,
                       )),
        AirbyteMessage(type=MessageType.TRACE,
                       trace=AirbyteTraceMessage(type=TraceType.STREAM_STATUS,
                                                 emitted_at=1577836800000.0,
                                                 error=None,
                                                 estimate=None,
                                                 stream_status=AirbyteStreamStatusTraceMessage(stream_descriptor=StreamDescriptor(name="stream"),
                                                                                               status=AirbyteStreamStatus(AirbyteStreamStatus.COMPLETE)))),
    ]

    assert messages == expected_messages
