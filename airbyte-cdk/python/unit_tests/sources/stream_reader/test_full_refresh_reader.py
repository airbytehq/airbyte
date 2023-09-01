#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock, call

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
from airbyte_cdk.sources.stream_reader.concurrent.concurrent_full_refresh_reader import ConcurrentFullRefreshStreamReader
from airbyte_cdk.sources.stream_reader.concurrent.partition_generator import PartitionGenerator
from airbyte_cdk.sources.stream_reader.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.stream_reader.synchronous_full_refresh_reader import SyncrhonousFullRefreshReader
from airbyte_cdk.sources.streams import FullRefreshStreamReader
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger

_A_CURSOR_FIELD = ["NESTED", "CURSOR"]
_DEFAULT_INTERNAL_CONFIG = InternalConfig()
_STREAM_NAME = "STREAM"


def _synchronous_reader():
    return SyncrhonousFullRefreshReader(DebugSliceLogger())


def _concurrent_reader():
    reader = ConcurrentFullRefreshStreamReader(PartitionGenerator, PartitionReader, 5, DebugSliceLogger())
    return reader


@pytest.mark.parametrize(
    "reader",
    [
        pytest.param(_synchronous_reader(), id="synchronous_reader"),
        pytest.param(_concurrent_reader(), id="concurrent_reader"),
    ],
)
def test_full_refresh_read_a_single_slice_with_debug(reader):
    logger = _mock_logger(True)

    partition = {"partition": 1}
    partitions = [partition]

    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    records_per_partition = [records]

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

    stream = _mock_stream(_STREAM_NAME, partitions, records_per_partition)

    actual_records = list(reader.read_stream(stream, _A_CURSOR_FIELD, logger, _DEFAULT_INTERNAL_CONFIG))

    assert expected_records == actual_records


@pytest.mark.parametrize(
    "reader",
    [
        pytest.param(_synchronous_reader(), id="synchronous_reader"),
        pytest.param(_concurrent_reader(), id="concurrent_reader"),
    ],
)
def test_full_refresh_read_a_single_slice(reader):
    logger = _mock_logger()

    partition = {"partition": 1}
    partitions = [partition]

    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    records_per_partition = [records]

    expected_records = [*records]

    stream = _mock_stream(_STREAM_NAME, partitions, records_per_partition)

    actual_records = list(reader.read_stream(stream, _A_CURSOR_FIELD, logger, _DEFAULT_INTERNAL_CONFIG))

    assert expected_records == actual_records

    expected_read_records_calls = [call(stream_slice=partition, sync_mode=SyncMode.full_refresh, cursor_field=_A_CURSOR_FIELD)]

    stream.read_records.assert_has_calls(expected_read_records_calls)


@pytest.mark.parametrize(
    "reader",
    [
        pytest.param(_synchronous_reader(), id="synchronous_reader"),
        pytest.param(_concurrent_reader(), id="concurrent_reader"),
    ],
)
def test_full_refresh_read_a_two_slices(reader):
    logger = _mock_logger()

    partition1 = {"partition": 1}
    partition2 = {"partition": 2}
    partitions = [partition1, partition2]

    records_partition_1 = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    records_partition_2 = [
        {"id": 3, "partition": 2},
        {"id": 4, "partition": 2},
    ]
    records_per_partition = [records_partition_1, records_partition_2]

    expected_records = [
        *records_partition_1,
        *records_partition_2,
    ]

    stream = _mock_stream(_STREAM_NAME, partitions, records_per_partition)

    actual_records = list(reader.read_stream(stream, _A_CURSOR_FIELD, logger, _DEFAULT_INTERNAL_CONFIG))

    for record in expected_records:
        assert record in actual_records
    assert len(expected_records) == len(actual_records)

    expected_read_records_calls = [
        call(sync_mode=SyncMode.full_refresh, cursor_field=_A_CURSOR_FIELD, stream_slice=partition1),
        call(sync_mode=SyncMode.full_refresh, cursor_field=_A_CURSOR_FIELD, stream_slice=partition2),
    ]
    actual_calls = stream.read_records.call_args_list

    for expected_call in expected_read_records_calls:
        assert expected_call in actual_calls
    assert len(expected_read_records_calls) == len(actual_calls)


@pytest.mark.parametrize(
    "reader",
    [
        pytest.param(_synchronous_reader(), id="synchronous_reader"),
        pytest.param(_concurrent_reader(), id="concurrent_reader"),
    ],
)
def test_only_read_up_to_limit(reader):
    logger = _mock_logger()

    internal_config = InternalConfig(_limit=1)

    partition = {"partition": 1}
    partitions = [partition]

    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    records_per_partition = [records]

    expected_records = records[:-1]

    stream = _mock_stream(_STREAM_NAME, partitions, records_per_partition)

    actual_records = list(reader.read_stream(stream, _A_CURSOR_FIELD, logger, internal_config))

    assert expected_records == actual_records

    expected_read_records_calls = [call(stream_slice=partition, sync_mode=SyncMode.full_refresh, cursor_field=_A_CURSOR_FIELD)]

    stream.read_records.assert_has_calls(expected_read_records_calls)


@pytest.mark.parametrize(
    "reader",
    [
        pytest.param(_synchronous_reader(), id="synchronous_reader"),
        pytest.param(_concurrent_reader(), id="concurrent_reader"),
    ],
)
def test_limit_only_considers_data(reader):
    logger = _mock_logger()

    internal_config = InternalConfig(_limit=2)

    partition = {"partition": 1}
    partitions = [partition]

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

    records_per_partition = [records]
    expected_records = records[:-1]

    stream = _mock_stream(_STREAM_NAME, partitions, records_per_partition)

    actual_records = list(reader.read_stream(stream, _A_CURSOR_FIELD, logger, internal_config))

    assert expected_records == actual_records

    expected_read_records_calls = [call(sync_mode=SyncMode.full_refresh, cursor_field=_A_CURSOR_FIELD, stream_slice=partition)]

    stream.read_records.assert_has_calls(expected_read_records_calls)


@pytest.mark.parametrize(
    "reader",
    [
        pytest.param(_synchronous_reader(), id="synchronous_reader"),
        pytest.param(_concurrent_reader(), id="concurrent_reader"),
    ],
)
def test_exception_is_raised_if_generate_partitions_fails(reader):
    logger = _mock_logger()

    partition = {"partition": 1}
    partitions = [partition]

    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    records_per_partition = [records]

    stream = _mock_stream(_STREAM_NAME, partitions, records_per_partition)
    stream.generate_partitions.side_effect = Mock(side_effect=RuntimeError("Test"))

    with pytest.raises(RuntimeError):
        list(reader.read_stream(stream, _A_CURSOR_FIELD, logger, _DEFAULT_INTERNAL_CONFIG))


@pytest.mark.parametrize(
    "reader",
    [
        pytest.param(_synchronous_reader(), id="synchronous_reader"),
        pytest.param(_concurrent_reader(), id="concurrent_reader"),
    ],
)
def test_exception_is_raised_if_read_records_fails(reader):
    logger = _mock_logger()

    partition = {"partition": 1}
    partitions = [partition]

    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]
    records_per_partition = [records]

    stream = _mock_stream(_STREAM_NAME, partitions, records_per_partition)
    stream.read_records.side_effect = Mock(side_effect=RuntimeError("Test"))

    with pytest.raises(RuntimeError):
        list(reader.read_stream(stream, _A_CURSOR_FIELD, logger, _DEFAULT_INTERNAL_CONFIG))


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
    actual_is_record = FullRefreshStreamReader.is_record(partition_record)
    assert actual_is_record == expected_is_record


def _mock_stream(name: str, partitions, records_per_partition, *, available=True, debug_log=False):
    stream = Mock()
    stream.name = name
    stream.get_json_schema.return_value = {}
    stream.generate_partitions.return_value = iter(partitions)
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
