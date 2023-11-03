#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent
import logging
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union
from unittest.mock import Mock

import freezegun
import pytest
from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Level,
    StreamDescriptor,
    SyncMode,
    TraceType,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import NoopCursor
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger
from airbyte_cdk.utils import AirbyteTracedException

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
        for record_or_exception in self._slice_to_records[stream_slice["partition"]]:
            if isinstance(record_or_exception, Exception):
                raise record_or_exception
            else:
                yield record_or_exception

    def get_json_schema(self) -> Mapping[str, Any]:
        return {}


class _MockSource(AbstractSource):

    message_repository = InMemoryMessageRepository()

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        pass

    def set_streams(self, streams):
        self._streams = streams

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return self._streams


class _MockConcurrentSource(ConcurrentSource):
    def __init__(self):
        super().__init__(1, 1)

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        pass

    def set_streams(self, streams):
        self._streams = streams

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return self._streams


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_concurrent_source_yields_the_same_messages_as_abstract_source_when_no_exceptions_are_raised():
    records_stream_1_partition_1 = [
        {"id": 1, "partition": "1"},
        {"id": 2, "partition": "1"},
    ]
    records_stream_1_partition_2 = [
        {"id": 3, "partition": "2"},
        {"id": 4, "partition": "2"},
    ]
    records_stream_2_partition_1 = [
        {"id": 100, "partition": "A"},
        {"id": 200, "partition": "A"},
    ]
    records_stream_2_partition_2 = [
        {"id": 300, "partition": "B"},
        {"id": 400, "partition": "B"},
    ]
    stream_1_slice_to_partition = {"1": records_stream_1_partition_1, "2": records_stream_1_partition_2}
    stream_2_slice_to_partition = {"A": records_stream_2_partition_1, "B": records_stream_2_partition_2}
    state = None

    logger = Mock()
    logger.level = logging.INFO
    logger.isEnabledFor.return_value = False
    # FIXME: probably also need to test to verify the slices can be logged!
    source, concurrent_source = _init_sources([stream_1_slice_to_partition, stream_2_slice_to_partition], state, logger)

    config = {}
    catalog = _create_configured_catalog(source._streams)
    messages_from_abstract_source = list(source.read(logger, config, catalog, state))
    messages_from_concurrent_source = list(concurrent_source.read(logger, config, catalog, state))

    expected_messages = [
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                error=None,
                estimate=None,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="stream0"), status=AirbyteStreamStatus(AirbyteStreamStatus.STARTED)
                ),
            ),
        ),
        # AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message='slice:{"partition": "1"}')),
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                error=None,
                estimate=None,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="stream0"), status=AirbyteStreamStatus(AirbyteStreamStatus.RUNNING)
                ),
            ),
        ),
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream="stream0",
                data=records_stream_1_partition_1[0],
                emitted_at=1577836800000,
            ),
        ),
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream="stream0",
                data=records_stream_1_partition_1[1],
                emitted_at=1577836800000,
            ),
        ),
        # AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message='slice:{"partition": "2"}')),
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream="stream0",
                data=records_stream_1_partition_2[0],
                emitted_at=1577836800000,
            ),
        ),
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream="stream0",
                data=records_stream_1_partition_2[1],
                emitted_at=1577836800000,
            ),
        ),
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                error=None,
                estimate=None,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="stream0"), status=AirbyteStreamStatus(AirbyteStreamStatus.COMPLETE)
                ),
            ),
        ),
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                error=None,
                estimate=None,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="stream1"), status=AirbyteStreamStatus(AirbyteStreamStatus.STARTED)
                ),
            ),
        ),
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                error=None,
                estimate=None,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="stream1"), status=AirbyteStreamStatus(AirbyteStreamStatus.RUNNING)
                ),
            ),
        ),
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream="stream1",
                data=records_stream_2_partition_1[0],
                emitted_at=1577836800000,
            ),
        ),
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream="stream1",
                data=records_stream_2_partition_1[1],
                emitted_at=1577836800000,
            ),
        ),
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream="stream1",
                data=records_stream_2_partition_2[0],
                emitted_at=1577836800000,
            ),
        ),
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream="stream1",
                data=records_stream_2_partition_2[1],
                emitted_at=1577836800000,
            ),
        ),
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                error=None,
                estimate=None,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="stream1"), status=AirbyteStreamStatus(AirbyteStreamStatus.COMPLETE)
                ),
            ),
        ),
    ]

    assert len(expected_messages) == len(messages_from_abstract_source)
    assert _compare(expected_messages, messages_from_abstract_source)

    # assert len(messages_from_abstract_source) == len(messages_from_concurrent_source)
    # assert messages_from_abstract_source == messages_from_concurrent_source
    assert _compare(messages_from_abstract_source, messages_from_concurrent_source)


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_concurrent_source_yields_the_same_messages_as_abstract_source_when_a_traced_exception_is_raised():
    records = [{"id": 1, "partition": "1"}, AirbyteTracedException()]
    stream_slice_to_partition = {"1": records}

    logger = Mock()
    logger.level = logging.INFO
    logger.isEnabledFor.return_value = False
    state = None
    source, concurrent_source = _init_sources([stream_slice_to_partition], state, logger)
    config = {}
    catalog = _create_configured_catalog(source._streams)
    messages_from_abstract_source = []
    try:
        for m in source.read(logger, config, catalog, state):
            messages_from_abstract_source.append(m)
    except AirbyteTracedException:
        # FIXME need to verify it
        pass
    messages_from_concurrent_source = []
    try:
        for m in concurrent_source.read(logger, config, catalog, state):
            messages_from_concurrent_source.append(m)
    except AirbyteTracedException:
        # FIXME need to verify it
        pass

    expected_messages = [
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                error=None,
                estimate=None,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="stream0"), status=AirbyteStreamStatus(AirbyteStreamStatus.STARTED)
                ),
            ),
        ),
        # AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message='slice:{"partition": "1"}')),
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                error=None,
                estimate=None,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="stream0"), status=AirbyteStreamStatus(AirbyteStreamStatus.RUNNING)
                ),
            ),
        ),
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream="stream0",
                data=records[0],
                emitted_at=1577836800000,
            ),
        ),
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                error=None,
                estimate=None,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="stream0"), status=AirbyteStreamStatus(AirbyteStreamStatus.INCOMPLETE)
                ),
            ),
        ),
    ]
    assert expected_messages == messages_from_abstract_source
    assert _compare(messages_from_abstract_source, messages_from_concurrent_source)


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_concurrent_source_yields_the_same_messages_as_abstract_source_when_an_exception_is_raised():
    records = [{"id": 1, "partition": "1"}, RuntimeError()]
    stream_slice_to_partition = {"1": records}
    logger = Mock()
    logger.level = logging.INFO
    logger.isEnabledFor.return_value = False

    state = None

    source, concurrent_source = _init_sources([stream_slice_to_partition], state, logger)
    config = {}
    catalog = _create_configured_catalog(source._streams)
    messages_from_abstract_source = []
    try:
        for m in source.read(logger, config, catalog, state):
            messages_from_abstract_source.append(m)
    except RuntimeError as e:
        # FIXME need to verify it
        pass
    messages_from_concurrent_source = []
    try:
        for m in concurrent_source.read(logger, config, catalog, state):
            messages_from_concurrent_source.append(m)
    except RuntimeError as e:
        # FIXME need to verify it
        pass

    expected_messages = [
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                error=None,
                estimate=None,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="stream0"), status=AirbyteStreamStatus(AirbyteStreamStatus.STARTED)
                ),
            ),
        ),
        # AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message='slice:{"partition": "1"}')),
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                error=None,
                estimate=None,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="stream0"), status=AirbyteStreamStatus(AirbyteStreamStatus.RUNNING)
                ),
            ),
        ),
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream="stream0",
                data=records[0],
                emitted_at=1577836800000,
            ),
        ),
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                error=None,
                estimate=None,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name="stream0"), status=AirbyteStreamStatus(AirbyteStreamStatus.INCOMPLETE)
                ),
            ),
        ),
    ]
    assert expected_messages == messages_from_abstract_source
    assert _compare(messages_from_abstract_source, messages_from_concurrent_source)

def _init_sources(stream_slice_to_partitions, state, logger):
    source = _init_source(stream_slice_to_partitions, state, logger, _MockSource())
    concurrent_source = _init_source(stream_slice_to_partitions, state, logger, _MockConcurrentSource())
    return source, concurrent_source
def _init_source(stream_slice_to_partitions, state, logger, source):
    cursor = NoopCursor()
    threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    streams = [
        StreamFacade.create_from_stream(_MockStream(stream_slices, f"stream{i}"), source, logger, threadpool, state, cursor)
        for i, stream_slices in enumerate(stream_slice_to_partitions)
    ]
    source.set_streams(streams)
    return source

def _create_configured_catalog(streams):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=s.name, json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                cursor_field=None,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
            for s in streams
        ]
    )
def _compare(s, t):
    # Use a compare method that does not require ordering or hashing the elements
    # We can't rely on the ordering because of the multithreading
    # AirbyteMessage does not implement __eq__ and __hash__
    t = list(t)
    try:
        for elem in s:
            t.remove(elem)
    except ValueError:
        return False
    return not t
