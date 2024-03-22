#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union
from unittest.mock import Mock

import freezegun
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
    TraceType,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import FinalStateCursor
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.utils import AirbyteTracedException
from unit_tests.sources.streams.concurrent.scenarios.thread_based_concurrent_stream_source_builder import NeverLogSliceLogger


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


class _MockConcurrentSource(ConcurrentSourceAdapter):
    message_repository = InMemoryMessageRepository()

    def __init__(self, logger):
        concurrent_source = ConcurrentSource.create(1, 1, logger, NeverLogSliceLogger(), self.message_repository)
        super().__init__(concurrent_source)

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
    logger = _init_logger()

    source, concurrent_source = _init_sources([stream_1_slice_to_partition, stream_2_slice_to_partition], state, logger)

    config = {}
    catalog = _create_configured_catalog(source._streams)
    messages_from_abstract_source = _read_from_source(source, logger, config, catalog, state, None)
    messages_from_concurrent_source = _read_from_source(concurrent_source, logger, config, catalog, state, None)

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
    _verify_messages(expected_messages, messages_from_abstract_source, messages_from_concurrent_source)


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_concurrent_source_yields_the_same_messages_as_abstract_source_when_a_traced_exception_is_raised():
    records = [{"id": 1, "partition": "1"}, AirbyteTracedException()]
    stream_slice_to_partition = {"1": records}

    logger = _init_logger()
    state = None
    source, concurrent_source = _init_sources([stream_slice_to_partition], state, logger)
    config = {}
    catalog = _create_configured_catalog(source._streams)
    messages_from_abstract_source = _read_from_source(source, logger, config, catalog, state, AirbyteTracedException)
    messages_from_concurrent_source = _read_from_source(concurrent_source, logger, config, catalog, state, AirbyteTracedException)

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
    _verify_messages(expected_messages, messages_from_abstract_source, messages_from_concurrent_source)


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_concurrent_source_yields_the_same_messages_as_abstract_source_when_an_exception_is_raised():
    records = [{"id": 1, "partition": "1"}, RuntimeError()]
    stream_slice_to_partition = {"1": records}
    logger = _init_logger()

    state = None

    source, concurrent_source = _init_sources([stream_slice_to_partition], state, logger)
    config = {}
    catalog = _create_configured_catalog(source._streams)
    messages_from_abstract_source = _read_from_source(source, logger, config, catalog, state, AirbyteTracedException)
    messages_from_concurrent_source = _read_from_source(concurrent_source, logger, config, catalog, state, RuntimeError)

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
    _verify_messages(expected_messages, messages_from_abstract_source, messages_from_concurrent_source)


def _init_logger():
    logger = Mock()
    logger.level = logging.INFO
    logger.isEnabledFor.return_value = False
    return logger


def _init_sources(stream_slice_to_partitions, state, logger):
    source = _init_source(stream_slice_to_partitions, state, logger, _MockSource())
    concurrent_source = _init_source(stream_slice_to_partitions, state, logger, _MockConcurrentSource(logger))
    return source, concurrent_source


def _init_source(stream_slice_to_partitions, state, logger, source):
    streams = [
        StreamFacade.create_from_stream(_MockStream(stream_slices, f"stream{i}"), source, logger, state, FinalStateCursor(stream_name=f"stream{i}", stream_namespace=None, message_repository=InMemoryMessageRepository()))
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


def _read_from_source(source, logger, config, catalog, state, expected_exception):
    messages = []
    try:
        for m in source.read(logger, config, catalog, state):
            messages.append(m)
    except Exception as e:
        if expected_exception:
            assert isinstance(e, expected_exception)
    return messages


def _verify_messages(expected_messages, messages_from_abstract_source, messages_from_concurrent_source):
    assert _compare(expected_messages, messages_from_concurrent_source)


def _compare(s, t):
    # Use a compare method that does not require ordering or hashing the elements
    # We can't rely on the ordering because of the multithreading
    # AirbyteMessage does not implement __eq__ and __hash__
    t = list(t)
    try:
        for elem in s:
            t.remove(elem)
    except ValueError:
        print(f"ValueError: {elem}")
        return False
    return not t
