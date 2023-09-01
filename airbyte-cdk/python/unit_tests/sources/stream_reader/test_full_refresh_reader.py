#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, List, Mapping, Optional, Union
from unittest.mock import Mock

import pytest
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteControlMessage,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteTraceMessage,
    ConnectorSpecification,
    Level,
    OrchestratorType,
    Status,
    SyncMode,
    TraceType,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.stream_reader.concurrent.concurrent_stream import ConcurrentStream
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger

_A_CURSOR_FIELD = ["NESTED", "CURSOR"]
_DEFAULT_INTERNAL_CONFIG = InternalConfig()
_STREAM_NAME = "STREAM"


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


def _legacy_stream(slice_to_partition_mapping):
    return _MockStream(slice_to_partition_mapping)


def _concurrent_stream(slice_to_partition_mapping):
    legacy_stream = _legacy_stream(slice_to_partition_mapping)
    return ConcurrentStream.create_from_legacy_stream(legacy_stream, 1)


@pytest.mark.parametrize(
    "constructor",
    [
        pytest.param(_legacy_stream, id="synchronous_reader"),
        pytest.param(_concurrent_stream, id="concurrent_reader"),
    ],
)
def test_full_refresh_read_a_single_slice_with_debug(constructor):
    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    slice_to_partition = {1: records}
    stream = constructor(slice_to_partition)
    logger = _mock_logger(True)
    slice_logger = DebugSliceLogger()

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

    actual_records = list(stream.read(_A_CURSOR_FIELD, logger, slice_logger, _DEFAULT_INTERNAL_CONFIG))

    assert expected_records == actual_records


@pytest.mark.parametrize(
    "constructor",
    [
        pytest.param(_legacy_stream, id="synchronous_reader"),
        pytest.param(_concurrent_stream, id="concurrent_reader"),
    ],
)
def test_full_refresh_read_a_single_slice(constructor):
    logger = _mock_logger()
    slice_logger = DebugSliceLogger()

    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    slice_to_partition = {1: records}
    stream = constructor(slice_to_partition)

    expected_records = [*records]

    actual_records = list(stream.read(_A_CURSOR_FIELD, logger, slice_logger, _DEFAULT_INTERNAL_CONFIG))

    assert expected_records == actual_records


@pytest.mark.parametrize(
    "constructor",
    [
        pytest.param(_legacy_stream, id="synchronous_reader"),
        pytest.param(_concurrent_stream, id="concurrent_reader"),
    ],
)
def test_full_refresh_read_a_two_slices(constructor):
    logger = _mock_logger()
    slice_logger = DebugSliceLogger()

    records_partition_1 = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    records_partition_2 = [
        {"id": 3, "partition": 2},
        {"id": 4, "partition": 2},
    ]
    slice_to_partition = {1: records_partition_1, 2: records_partition_2}
    stream = constructor(slice_to_partition)

    expected_records = [
        *records_partition_1,
        *records_partition_2,
    ]

    actual_records = list(stream.read(_A_CURSOR_FIELD, logger, slice_logger, _DEFAULT_INTERNAL_CONFIG))

    for record in expected_records:
        assert record in actual_records
    assert len(expected_records) == len(actual_records)


@pytest.mark.parametrize(
    "constructor",
    [
        pytest.param(_legacy_stream, id="synchronous_reader"),
        pytest.param(_concurrent_stream, id="concurrent_reader"),
    ],
)
def test_only_read_up_to_limit(constructor):
    logger = _mock_logger()
    slice_logger = DebugSliceLogger()

    internal_config = InternalConfig(_limit=1)

    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    slice_to_partition = {1: records}
    stream = constructor(slice_to_partition)

    expected_records = records[:-1]

    actual_records = list(stream.read(_A_CURSOR_FIELD, logger, slice_logger, internal_config))

    assert expected_records == actual_records


@pytest.mark.parametrize(
    "constructor",
    [
        pytest.param(_legacy_stream, id="synchronous_reader"),
        pytest.param(_concurrent_stream, id="concurrent_reader"),
    ],
)
def test_limit_only_considers_data(constructor):
    logger = _mock_logger()
    slice_logger = DebugSliceLogger()

    internal_config = InternalConfig(_limit=2)

    records = [
        AirbyteMessage(
            type=MessageType.LOG,
            log=AirbyteLogMessage(
                level=Level.INFO,
                message="A_LOG_MESSAGE",
            ),
        ),
        {"id": 1, "partition": 1},
        AirbyteMessage(
            type=MessageType.LOG,
            log=AirbyteLogMessage(
                level=Level.INFO,
                message="ANOTHER_LOG_MESSAGE",
            ),
        ),
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                data={"id": 2, "partition": 1},
                stream=_STREAM_NAME,
                emitted_at=1,
            ),
        ),
        {"id": 2, "partition": 1},
    ]

    slice_to_partition = {1: records}
    stream = constructor(slice_to_partition)
    expected_records = records[:-1]

    actual_records = list(stream.read(_A_CURSOR_FIELD, logger, slice_logger, internal_config))

    assert expected_records == actual_records


@pytest.mark.parametrize(
    "partition_record, expected_is_record",
    [
        pytest.param({"id": 1}, True, id="a_dict_is_a_record"),
        pytest.param(
            AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(stream="S", data={}, emitted_at=1)),
            True,
            id="an_airbyte_record_is_a_record",
        ),
        pytest.param(
            AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message="A_MESSAGE")),
            False,
            id="an_airbyte_log_is_not_a_record",
        ),
        pytest.param(AirbyteMessage(type=MessageType.STATE, state=AirbyteStateMessage()), False, id="an_airbyte_state_is_not_a_record"),
        pytest.param(
            AirbyteMessage(type=MessageType.CATALOG, catalog=AirbyteCatalog(streams=[])), False, id="an_airbyte_catalog_is_not_a_record"
        ),
        pytest.param(
            AirbyteMessage(type=MessageType.SPEC, spec=ConnectorSpecification(connectionSpecification={})),
            False,
            id="an_airbyte_spec_is_not_a_record",
        ),
        pytest.param(
            AirbyteMessage(type=MessageType.CONNECTION_STATUS, connectionStatus=AirbyteConnectionStatus(status=Status.SUCCEEDED)),
            False,
            id="an_airbyte_connection_status_is_not_a_record",
        ),
        pytest.param(
            AirbyteMessage(type=MessageType.CONTROL, control=AirbyteControlMessage(type=OrchestratorType.CONNECTOR_CONFIG, emitted_at=1.0)),
            False,
            id="an_airbyte_control_message_is_not_a_record",
        ),
        pytest.param(
            AirbyteMessage(type=MessageType.TRACE, trace=AirbyteTraceMessage(type=TraceType.ERROR, emitted_at=1.0)),
            False,
            id="an_airbyte_trace_message_is_not_a_record",
        ),
        pytest.param("not a record", False, id="a_string_is_not_a_record"),
        pytest.param(None, False, id="none_is_not_a_record"),
    ],
)
def test_is_record(partition_record, expected_is_record):
    actual_is_record = AbstractStream.is_record(partition_record)
    assert actual_is_record == expected_is_record


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
    return logger
