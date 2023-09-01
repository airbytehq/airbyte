#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

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
    TraceType,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.streams.abstract_stream import AbstractStream


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
