#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from unittest.mock import Mock

import pytest
from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Level,
    StreamDescriptor,
    SyncMode,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor, FinalStateCursor
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger

_A_CURSOR_FIELD = ["NESTED", "CURSOR"]
_DEFAULT_INTERNAL_CONFIG = InternalConfig()
_STREAM_NAME = "STREAM"
_NO_STATE = None


class _MockStream(Stream):
    def __init__(self, slice_to_records: Mapping[str, List[Mapping[str, Any]]]):
        self._slice_to_records = slice_to_records

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


class MockConcurrentCursor(Cursor):
    _state: MutableMapping[str, Any]
    _message_repository: MessageRepository

    def __init__(self, message_repository: MessageRepository):
        self._message_repository = message_repository
        self._state = {}

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    def observe(self, record: Record) -> None:
        partition = str(record.data.get("partition"))
        timestamp = record.data.get("created_at")
        self._state[partition] = {"created_at": timestamp}

    def close_partition(self, partition: Partition) -> None:
        self._message_repository.emit_message(
            AirbyteMessage(
                type=MessageType.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name='__mock_stream', namespace=None),
                        stream_state=AirbyteStateBlob(**self._state),
                    )
                ),
            )
        )

    def ensure_at_least_one_state_emitted(self) -> None:
        pass


def _stream(slice_to_partition_mapping, slice_logger, logger, message_repository):
    return _MockStream(slice_to_partition_mapping)


def _concurrent_stream(slice_to_partition_mapping, slice_logger, logger, message_repository, cursor: Optional[Cursor] = None):
    stream = _stream(slice_to_partition_mapping, slice_logger, logger, message_repository)
    cursor = cursor or FinalStateCursor(stream_name=stream.name, stream_namespace=stream.namespace, message_repository=message_repository)
    source = Mock()
    source._slice_logger = slice_logger
    source.message_repository = message_repository
    stream = StreamFacade.create_from_stream(stream, source, logger, _NO_STATE, cursor)
    stream.logger.setLevel(logger.level)
    return stream


def _incremental_stream(slice_to_partition_mapping, slice_logger, logger, message_repository, timestamp):
    stream = _stream(slice_to_partition_mapping, slice_logger, logger, message_repository)
    stream.state = {"created_at": timestamp}
    return stream


def _incremental_concurrent_stream(slice_to_partition_mapping, slice_logger, logger, message_repository, cursor):
    stream = _concurrent_stream(slice_to_partition_mapping, slice_logger, logger, message_repository, cursor)
    return stream


@pytest.mark.parametrize(
    "constructor",
    [
        pytest.param(_stream, id="synchronous_reader"),
        pytest.param(_concurrent_stream, id="concurrent_reader"),
    ],
)
def test_full_refresh_read_a_single_slice_with_debug(constructor):
    # This test verifies that a concurrent stream adapted from a Stream behaves the same as the Stream object.
    # It is done by running the same test cases on both streams
    configured_stream = ConfiguredAirbyteStream(stream=AirbyteStream(name="mock_stream", supported_sync_modes=[SyncMode.full_refresh], json_schema={}), sync_mode=SyncMode.full_refresh,destination_sync_mode=DestinationSyncMode.overwrite)
    internal_config = InternalConfig()
    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    slice_to_partition = {1: records}
    slice_logger = DebugSliceLogger()
    logger = _mock_logger(True)
    message_repository = InMemoryMessageRepository(Level.DEBUG)
    stream = constructor(slice_to_partition, slice_logger, logger, message_repository)
    state_manager = ConnectorStateManager(stream_instance_map={})

    expected_records = [
        AirbyteMessage(
            type=MessageType.LOG,
            log=AirbyteLogMessage(
                level=Level.INFO,
                message='slice:{"partition": 1}',
            ),
        ),
        *records,
    ]

    # Temporary check to only validate the final state message for synchronous sources since it has not been implemented for concurrent yet
    if constructor == _stream:
        expected_records.append(
            AirbyteMessage(
                type=MessageType.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name='__mock_stream', namespace=None),
                        stream_state=AirbyteStateBlob(__ab_full_refresh_state_message=True),
                    )
                ),
            ),
        )

    actual_records = _read(stream, configured_stream, logger, slice_logger, message_repository, state_manager, internal_config)

    assert expected_records == actual_records


@pytest.mark.parametrize(
    "constructor",
    [
        pytest.param(_stream, id="synchronous_reader"),
        pytest.param(_concurrent_stream, id="concurrent_reader"),
    ],
)
def test_full_refresh_read_a_single_slice(constructor):
    # This test verifies that a concurrent stream adapted from a Stream behaves the same as the Stream object.
    # It is done by running the same test cases on both streams
    configured_stream = ConfiguredAirbyteStream(stream=AirbyteStream(name="mock_stream", supported_sync_modes=[SyncMode.full_refresh], json_schema={}), sync_mode=SyncMode.full_refresh,destination_sync_mode=DestinationSyncMode.overwrite)
    internal_config = InternalConfig()
    logger = _mock_logger()
    slice_logger = DebugSliceLogger()
    message_repository = InMemoryMessageRepository(Level.INFO)
    state_manager = ConnectorStateManager(stream_instance_map={})

    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    slice_to_partition = {1: records}
    stream = constructor(slice_to_partition, slice_logger, logger, message_repository)

    expected_records = [*records]

    # Temporary check to only validate the final state message for synchronous sources since it has not been implemented for concurrent yet
    if constructor == _stream:
        expected_records.append(
            AirbyteMessage(
                type=MessageType.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name='__mock_stream', namespace=None),
                        stream_state=AirbyteStateBlob(__ab_full_refresh_state_message=True),
                    )
                ),
            ),
        )

    actual_records = _read(stream, configured_stream, logger, slice_logger, message_repository, state_manager, internal_config)

    assert expected_records == actual_records


@pytest.mark.parametrize(
    "constructor",
    [
        pytest.param(_stream, id="synchronous_reader"),
        pytest.param(_concurrent_stream, id="concurrent_reader"),
    ],
)
def test_full_refresh_read_a_two_slices(constructor):
    # This test verifies that a concurrent stream adapted from a Stream behaves the same as the Stream object
    # It is done by running the same test cases on both streams
    configured_stream = ConfiguredAirbyteStream(stream=AirbyteStream(name="mock_stream", supported_sync_modes=[SyncMode.full_refresh], json_schema={}), sync_mode=SyncMode.full_refresh,destination_sync_mode=DestinationSyncMode.overwrite)
    internal_config = InternalConfig()
    logger = _mock_logger()
    slice_logger = DebugSliceLogger()
    message_repository = InMemoryMessageRepository(Level.INFO)
    state_manager = ConnectorStateManager(stream_instance_map={})

    records_partition_1 = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    records_partition_2 = [
        {"id": 3, "partition": 2},
        {"id": 4, "partition": 2},
    ]
    slice_to_partition = {1: records_partition_1, 2: records_partition_2}
    stream = constructor(slice_to_partition, slice_logger, logger, message_repository)

    expected_records = [
        *records_partition_1,
        *records_partition_2,
    ]

    # Temporary check to only validate the final state message for synchronous sources since it has not been implemented for concurrent yet
    if constructor == _stream:
        expected_records.append(
            AirbyteMessage(
                type=MessageType.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name='__mock_stream', namespace=None),
                        stream_state=AirbyteStateBlob(__ab_full_refresh_state_message=True),
                    )
                ),
            ),
        )

    actual_records = _read(stream, configured_stream, logger, slice_logger, message_repository, state_manager, internal_config)

    for record in expected_records:
        assert record in actual_records
    assert len(expected_records) == len(actual_records)


def test_incremental_read_two_slices():
    # This test verifies that a stream running in incremental mode emits state messages correctly
    configured_stream = ConfiguredAirbyteStream(stream=AirbyteStream(name="mock_stream", supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental], json_schema={}), sync_mode=SyncMode.incremental,destination_sync_mode=DestinationSyncMode.overwrite)
    internal_config = InternalConfig()
    logger = _mock_logger()
    slice_logger = DebugSliceLogger()
    message_repository = InMemoryMessageRepository(Level.INFO)
    state_manager = ConnectorStateManager(stream_instance_map={})
    timestamp = "1708899427"

    records_partition_1 = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    records_partition_2 = [
        {"id": 3, "partition": 2},
        {"id": 4, "partition": 2},
    ]
    slice_to_partition = {1: records_partition_1, 2: records_partition_2}
    stream = _incremental_stream(slice_to_partition, slice_logger, logger, message_repository, timestamp)

    expected_records = [
        *records_partition_1,
        _create_state_message("__mock_stream", {"created_at": timestamp}),
        *records_partition_2,
        _create_state_message("__mock_stream", {"created_at": timestamp})
    ]

    actual_records = _read(stream, configured_stream, logger, slice_logger, message_repository, state_manager, internal_config)

    for record in expected_records:
        assert record in actual_records
    assert len(expected_records) == len(actual_records)


def test_concurrent_incremental_read_two_slices():
    # This test verifies that an incremental concurrent stream manages state correctly for multiple slices syncing concurrently
    configured_stream = ConfiguredAirbyteStream(stream=AirbyteStream(name="mock_stream", supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental], json_schema={}), sync_mode=SyncMode.incremental,destination_sync_mode=DestinationSyncMode.overwrite)
    internal_config = InternalConfig()
    logger = _mock_logger()
    slice_logger = DebugSliceLogger()
    message_repository = InMemoryMessageRepository(Level.INFO)
    state_manager = ConnectorStateManager(stream_instance_map={})
    slice_timestamp_1 = "1708850000"
    slice_timestamp_2 = "1708950000"
    cursor = MockConcurrentCursor(message_repository)

    records_partition_1 = [
        {"id": 1, "partition": 1, "created_at": "1708800000"},
        {"id": 2, "partition": 1, "created_at": slice_timestamp_1},
    ]
    records_partition_2 = [
        {"id": 3, "partition": 2, "created_at": "1708900000"},
        {"id": 4, "partition": 2, "created_at": slice_timestamp_2},
    ]
    slice_to_partition = {1: records_partition_1, 2: records_partition_2}
    stream = _incremental_concurrent_stream(slice_to_partition, slice_logger, logger, message_repository, cursor)

    expected_records = [
        *records_partition_1,
        *records_partition_2,
    ]

    expected_state = _create_state_message("__mock_stream", {"1": {"created_at": slice_timestamp_1}, "2": {"created_at": slice_timestamp_2}})

    actual_records = _read(stream, configured_stream, logger, slice_logger, message_repository, state_manager, internal_config)

    for record in expected_records:
        assert record in actual_records
    assert len(expected_records) == len(actual_records)

    # We don't have a real source that reads from the message_repository for state, so we read from the queue directly to verify
    # the cursor observed records correctly and updated partition states
    mock_partition = Mock()
    cursor.close_partition(mock_partition)
    actual_state = [state for state in message_repository.consume_queue()]
    assert len(actual_state) == 1
    assert actual_state[0] == expected_state


def _read(stream, configured_stream, logger, slice_logger, message_repository, state_manager, internal_config):
    records = []
    for record in stream.read(configured_stream, logger, slice_logger, {}, state_manager, internal_config):
        for message in message_repository.consume_queue():
            records.append(message)
        records.append(record)
    return records


def _mock_partition_generator(name: str, slices, records_per_partition, *, available=True, debug_log=False):
    stream = Mock()
    stream.name = name
    stream.get_json_schema.return_value = {}
    stream.generate_partitions.return_value = iter(slices)
    stream.read_records.side_effect = [iter(records) for records in records_per_partition]
    stream.logger.isEnabledFor.return_value = debug_log
    if available:
        stream.check_availability.return_value = True, None
    else:
        stream.check_availability.return_value = False, "A reason why the stream is unavailable"
    return stream


def _mock_logger(enabled_for_debug=False):
    logger = Mock()
    logger.isEnabledFor.return_value = enabled_for_debug
    logger.level = logging.DEBUG if enabled_for_debug else logging.INFO
    return logger


def _create_state_message(stream: str, state: Mapping[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(
        type=MessageType.STATE,
        state=AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name=stream, namespace=None),
                stream_state=AirbyteStateBlob(**state),
            )
        ),
    )
