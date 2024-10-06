#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union
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
from airbyte_cdk.sources.streams.core import CheckpointMixin, StreamData
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger

_A_CURSOR_FIELD = ["NESTED", "CURSOR"]
_DEFAULT_INTERNAL_CONFIG = InternalConfig()
_STREAM_NAME = "STREAM"
_NO_STATE = None


class _MockStream(Stream):
    def __init__(self, slice_to_records: Mapping[str, List[Mapping[str, Any]]], json_schema: Dict[str, Any] = None):
        self._slice_to_records = slice_to_records
        self._mocked_json_schema = json_schema or {}

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return None

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for partition in self._slice_to_records.keys():
            yield {"partition_key": partition}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        yield from self._slice_to_records[stream_slice["partition_key"]]

    def get_json_schema(self) -> Mapping[str, Any]:
        return self._mocked_json_schema


class _MockIncrementalStream(_MockStream, CheckpointMixin):
    _state = {}

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        """State setter, accept state serialized by state getter."""
        self._state = value

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return ["created_at"]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        cursor = self.cursor_field[0]
        for record in self._slice_to_records[stream_slice["partition_key"]]:
            yield record
            if cursor not in self._state:
                self._state[cursor] = record.get(cursor)
            else:
                self._state[cursor] = max(self._state[cursor], record.get(cursor))


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
                        stream_descriptor=StreamDescriptor(name="__mock_stream", namespace=None),
                        stream_state=AirbyteStateBlob(**self._state),
                    ),
                ),
            )
        )

    def ensure_at_least_one_state_emitted(self) -> None:
        pass


def _stream(slice_to_partition_mapping, slice_logger, logger, message_repository, json_schema=None):
    return _MockStream(slice_to_partition_mapping, json_schema=json_schema)


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
    stream = _MockIncrementalStream(slice_to_partition_mapping)
    return stream


def _incremental_concurrent_stream(slice_to_partition_mapping, slice_logger, logger, message_repository, cursor):
    stream = _concurrent_stream(slice_to_partition_mapping, slice_logger, logger, message_repository, cursor)
    return stream


def _stream_with_no_cursor_field(slice_to_partition_mapping, slice_logger, logger, message_repository):
    def get_updated_state(current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> MutableMapping[str, Any]:
        raise Exception("I shouldn't be invoked by a full_refresh stream")

    mock_stream = _MockStream(slice_to_partition_mapping)
    mock_stream.get_updated_state = get_updated_state
    return mock_stream


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
    configured_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="mock_stream", supported_sync_modes=[SyncMode.full_refresh], json_schema={}),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
    internal_config = InternalConfig()
    records = [
        {"id": 1, "partition_key": 1},
        {"id": 2, "partition_key": 1},
    ]
    slice_to_partition = {1: records}
    slice_logger = DebugSliceLogger()
    logger = _mock_logger(True)
    message_repository = InMemoryMessageRepository(Level.DEBUG)
    stream = constructor(slice_to_partition, slice_logger, logger, message_repository)
    state_manager = ConnectorStateManager()

    expected_records = [
        AirbyteMessage(
            type=MessageType.LOG,
            log=AirbyteLogMessage(
                level=Level.INFO,
                message='slice:{"partition_key": 1}',
            ),
        ),
        *records,
    ]

    # Synchronous streams emit a final state message to indicate that the stream has finished reading
    # Concurrent streams don't emit their own state messages - the concurrent source observes the cursor
    # and emits the state messages. Therefore, we can only check the value of the cursor's state at the end
    if constructor == _stream:
        expected_records.append(
            AirbyteMessage(
                type=MessageType.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="__mock_stream", namespace=None),
                        stream_state=AirbyteStateBlob(__ab_no_cursor_state_message=True),
                    ),
                ),
            ),
        )

    actual_records = _read(stream, configured_stream, logger, slice_logger, message_repository, state_manager, internal_config)

    if constructor == _concurrent_stream:
        assert hasattr(stream._cursor, "state")
        assert str(stream._cursor.state) == "{'__ab_no_cursor_state_message': True}"

    assert actual_records == expected_records


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
    configured_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="mock_stream", supported_sync_modes=[SyncMode.full_refresh], json_schema={}),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
    internal_config = InternalConfig()
    logger = _mock_logger()
    slice_logger = DebugSliceLogger()
    message_repository = InMemoryMessageRepository(Level.INFO)
    state_manager = ConnectorStateManager()

    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    slice_to_partition = {1: records}
    stream = constructor(slice_to_partition, slice_logger, logger, message_repository)

    expected_records = [*records]

    # Synchronous streams emit a final state message to indicate that the stream has finished reading
    # Concurrent streams don't emit their own state messages - the concurrent source observes the cursor
    # and emits the state messages. Therefore, we can only check the value of the cursor's state at the end
    if constructor == _stream:
        expected_records.append(
            AirbyteMessage(
                type=MessageType.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="__mock_stream", namespace=None),
                        stream_state=AirbyteStateBlob(__ab_no_cursor_state_message=True),
                    ),
                ),
            ),
        )

    actual_records = _read(stream, configured_stream, logger, slice_logger, message_repository, state_manager, internal_config)

    if constructor == _concurrent_stream:
        assert hasattr(stream._cursor, "state")
        assert str(stream._cursor.state) == "{'__ab_no_cursor_state_message': True}"

    assert actual_records == expected_records


@pytest.mark.parametrize(
    "constructor",
    [
        pytest.param(_stream, id="synchronous_reader"),
        pytest.param(_concurrent_stream, id="concurrent_reader"),
        pytest.param(_stream_with_no_cursor_field, id="no_cursor_field"),
    ],
)
def test_full_refresh_read_two_slices(constructor):
    # This test verifies that a concurrent stream adapted from a Stream behaves the same as the Stream object
    # It is done by running the same test cases on both streams
    configured_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="mock_stream", supported_sync_modes=[SyncMode.full_refresh], json_schema={}),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
    internal_config = InternalConfig()
    logger = _mock_logger()
    slice_logger = DebugSliceLogger()
    message_repository = InMemoryMessageRepository(Level.INFO)
    state_manager = ConnectorStateManager()

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

    # Synchronous streams emit a final state message to indicate that the stream has finished reading
    # Concurrent streams don't emit their own state messages - the concurrent source observes the cursor
    # and emits the state messages. Therefore, we can only check the value of the cursor's state at the end
    if constructor == _stream or constructor == _stream_with_no_cursor_field:
        expected_records.append(
            AirbyteMessage(
                type=MessageType.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="__mock_stream", namespace=None),
                        stream_state=AirbyteStateBlob(__ab_no_cursor_state_message=True),
                    ),
                ),
            ),
        )

    actual_records = _read(stream, configured_stream, logger, slice_logger, message_repository, state_manager, internal_config)

    if constructor == _concurrent_stream:
        assert hasattr(stream._cursor, "state")
        assert str(stream._cursor.state) == "{'__ab_no_cursor_state_message': True}"

    for record in expected_records:
        assert record in actual_records
    assert len(actual_records) == len(expected_records)


def test_incremental_read_two_slices():
    # This test verifies that a stream running in incremental mode emits state messages correctly
    configured_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="mock_stream", supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental], json_schema={}),
        sync_mode=SyncMode.incremental,
        cursor_field=["created_at"],
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
    internal_config = InternalConfig()
    logger = _mock_logger()
    slice_logger = DebugSliceLogger()
    message_repository = InMemoryMessageRepository(Level.INFO)
    state_manager = ConnectorStateManager()
    timestamp = "1708899427"

    records_partition_1 = [
        {"id": 1, "partition": 1, "created_at": "1708899000"},
        {"id": 2, "partition": 1, "created_at": "1708899000"},
    ]
    records_partition_2 = [
        {"id": 3, "partition": 2, "created_at": "1708899400"},
        {"id": 4, "partition": 2, "created_at": "1708899427"},
    ]
    slice_to_partition = {1: records_partition_1, 2: records_partition_2}
    stream = _incremental_stream(slice_to_partition, slice_logger, logger, message_repository, timestamp)

    expected_records = [
        *records_partition_1,
        _create_state_message("__mock_incremental_stream", {"created_at": timestamp}),
        *records_partition_2,
        _create_state_message("__mock_incremental_stream", {"created_at": timestamp}),
    ]

    actual_records = _read(stream, configured_stream, logger, slice_logger, message_repository, state_manager, internal_config)

    for record in expected_records:
        assert record in actual_records
    assert len(actual_records) == len(expected_records)


def test_concurrent_incremental_read_two_slices():
    # This test verifies that an incremental concurrent stream manages state correctly for multiple slices syncing concurrently
    configured_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="mock_stream", supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental], json_schema={}),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
    internal_config = InternalConfig()
    logger = _mock_logger()
    slice_logger = DebugSliceLogger()
    message_repository = InMemoryMessageRepository(Level.INFO)
    state_manager = ConnectorStateManager()
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

    expected_state = _create_state_message(
        "__mock_stream", {"1": {"created_at": slice_timestamp_1}, "2": {"created_at": slice_timestamp_2}}
    )

    actual_records = _read(stream, configured_stream, logger, slice_logger, message_repository, state_manager, internal_config)

    for record in expected_records:
        assert record in actual_records
    assert len(actual_records) == len(expected_records)

    # We don't have a real source that reads from the message_repository for state, so we read from the queue directly to verify
    # the cursor observed records correctly and updated partition states
    mock_partition = Mock()
    cursor.close_partition(mock_partition)
    actual_state = [state for state in message_repository.consume_queue()]
    assert len(actual_state) == 1
    assert actual_state[0] == expected_state


def setup_stream_dependencies(configured_json_schema):
    configured_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="mock_stream", supported_sync_modes=[SyncMode.full_refresh], json_schema=configured_json_schema),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
    internal_config = InternalConfig()
    logger = _mock_logger()
    slice_logger = DebugSliceLogger()
    message_repository = InMemoryMessageRepository(Level.INFO)
    state_manager = ConnectorStateManager()
    return configured_stream, internal_config, logger, slice_logger, message_repository, state_manager


def test_configured_json_schema():
    current_json_schema = {
        "$schema": "https://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "id": {"type": ["null", "number"]},
            "name": {"type": ["null", "string"]},
        },
    }

    configured_stream, internal_config, logger, slice_logger, message_repository, state_manager = setup_stream_dependencies(
        current_json_schema
    )
    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]

    slice_to_partition = {1: records}
    stream = _stream(slice_to_partition, slice_logger, logger, message_repository, json_schema=current_json_schema)
    assert not stream.configured_json_schema
    _read(stream, configured_stream, logger, slice_logger, message_repository, state_manager, internal_config)
    assert stream.configured_json_schema == current_json_schema


def test_configured_json_schema_with_invalid_properties():
    """
    Configured Schemas can have very old fields, so we need to housekeeping ourselves.
    The purpose of this test in ensure that correct cleanup occurs when configured catalog schema is compared with current stream schema.
    """
    old_user_insights = "old_user_insights"
    old_feature_info = "old_feature_info"
    configured_json_schema = {
        "$schema": "https://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "id": {"type": ["null", "number"]},
            "name": {"type": ["null", "string"]},
            "cost_per_conversation": {"type": ["null", "string"]},
            old_user_insights: {"type": ["null", "string"]},
            old_feature_info: {"type": ["null", "string"]},
        },
    }
    # stream schema is updated e.g. some fields in new api version are deprecated
    stream_schema = deepcopy(configured_json_schema)
    del stream_schema["properties"][old_user_insights]
    del stream_schema["properties"][old_feature_info]

    configured_stream, internal_config, logger, slice_logger, message_repository, state_manager = setup_stream_dependencies(
        configured_json_schema
    )
    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]

    slice_to_partition = {1: records}
    stream = _stream(slice_to_partition, slice_logger, logger, message_repository, json_schema=stream_schema)
    assert not stream.configured_json_schema
    _read(stream, configured_stream, logger, slice_logger, message_repository, state_manager, internal_config)
    assert stream.configured_json_schema != configured_json_schema
    configured_json_schema_properties = stream.configured_json_schema["properties"]
    assert old_user_insights not in configured_json_schema_properties
    assert old_feature_info not in configured_json_schema_properties
    for stream_schema_property in stream_schema["properties"]:
        assert (
            stream_schema_property in configured_json_schema_properties
        ), f"Stream schema property: {stream_schema_property} missing in configured schema"
        assert stream_schema["properties"][stream_schema_property] == configured_json_schema_properties[stream_schema_property]


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
            ),
        ),
    )
