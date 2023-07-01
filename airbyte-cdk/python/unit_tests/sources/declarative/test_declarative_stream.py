#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest import mock
from unittest.mock import MagicMock, call

from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteTraceMessage,
    Level,
    SyncMode,
    TraceType,
    Type,
)
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.transformations import AddFields, RecordTransformation
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from airbyte_cdk.sources.declarative.types import Record

SLICE_NOT_CONSIDERED_FOR_EQUALITY = {}


def test_declarative_stream():
    name = "stream"
    primary_key = "pk"
    cursor_field = "created_at"

    schema_loader = MagicMock()
    json_schema = {"name": {"type": "string"}}
    schema_loader.get_json_schema.return_value = json_schema

    state = MagicMock()
    records = [
        {"pk": 1234, "field": "value"},
        {"pk": 4567, "field": "different_value"},
        AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="This is a log  message")),
        AirbyteMessage(type=Type.TRACE, trace=AirbyteTraceMessage(type=TraceType.ERROR, emitted_at=12345)),
    ]
    stream_slices = [
        {"date": "2021-01-01"},
        {"date": "2021-01-02"},
        {"date": "2021-01-03"},
    ]

    retriever = MagicMock()
    retriever.state = state
    retriever.read_records.return_value = records
    retriever.stream_slices.return_value = stream_slices

    no_op_transform = mock.create_autospec(spec=RecordTransformation)
    no_op_transform.transform = MagicMock(side_effect=lambda record, config, stream_slice, stream_state: record)
    transformations = [no_op_transform]

    config = {"api_key": "open_sesame"}

    stream = DeclarativeStream(
        name=name,
        primary_key=primary_key,
        stream_cursor_field="{{ parameters['cursor_field'] }}",
        schema_loader=schema_loader,
        retriever=retriever,
        config=config,
        transformations=transformations,
        parameters={"cursor_field": "created_at"},
    )

    assert stream.name == name
    assert stream.get_json_schema() == json_schema
    assert stream.state == state
    input_slice = stream_slices[0]
    assert list(stream.read_records(SyncMode.full_refresh, cursor_field, input_slice, state)) == records
    assert stream.primary_key == primary_key
    assert stream.cursor_field == cursor_field
    assert stream.stream_slices(sync_mode=SyncMode.incremental, cursor_field=cursor_field, stream_state=None) == stream_slices
    for transformation in transformations:
        expected_calls = [
            call(record, config=config, stream_slice=input_slice, stream_state=state) for record in records if isinstance(record, dict)
        ]
        assert len(transformation.transform.call_args_list) == len(expected_calls)
        transformation.transform.assert_has_calls(expected_calls, any_order=False)


def test_declarative_stream_with_add_fields_transform():
    name = "stream"
    primary_key = "pk"
    cursor_field = "created_at"

    schema_loader = MagicMock()
    json_schema = {"name": {"type": "string"}}
    schema_loader.get_json_schema.return_value = json_schema

    state = MagicMock()
    stream_slices = [
        {"date": "2021-01-01"},
        {"date": "2021-01-02"},
        {"date": "2021-01-03"},
    ]
    input_slice = stream_slices[0]

    retriever_records = [
        {"pk": 1234, "field": "value"},
        Record({"pk": 4567, "field": "different_value"}, input_slice),
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(data={"pk": 1357, "field": "a_value"}, emitted_at=12344, stream="stream")),
        AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="This is a log  message")),
        AirbyteMessage(type=Type.TRACE, trace=AirbyteTraceMessage(type=TraceType.ERROR, emitted_at=12345)),
    ]

    expected_records = [
        {"pk": 1234, "field": "value", "added_key": "added_value"},
        {"pk": 4567, "field": "different_value", "added_key": "added_value"},
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(data={"pk": 1357, "field": "a_value", "added_key": "added_value"}, emitted_at=12344, stream="stream")),
        AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="This is a log  message")),
        AirbyteMessage(type=Type.TRACE, trace=AirbyteTraceMessage(type=TraceType.ERROR, emitted_at=12345)),
    ]

    retriever = MagicMock()
    retriever.state = state
    retriever.read_records.return_value = retriever_records
    retriever.stream_slices.return_value = stream_slices

    inputs = [AddedFieldDefinition(path=["added_key"], value="added_value", parameters={})]
    add_fields_transform = AddFields(fields=inputs, parameters={})
    transformations = [add_fields_transform]

    config = {"api_key": "open_sesame"}

    stream = DeclarativeStream(
        name=name,
        primary_key=primary_key,
        stream_cursor_field="{{ parameters['cursor_field'] }}",
        schema_loader=schema_loader,
        retriever=retriever,
        config=config,
        transformations=transformations,
        parameters={"cursor_field": "created_at"},
    )

    assert stream.name == name
    assert stream.get_json_schema() == json_schema
    assert stream.state == state
    assert list(stream.read_records(SyncMode.full_refresh, cursor_field, input_slice, state)) == expected_records


def test_state_checkpoint_interval():
    stream = DeclarativeStream(
        name="any name",
        primary_key="any primary key",
        stream_cursor_field="{{ parameters['cursor_field'] }}",
        schema_loader=MagicMock(),
        retriever=MagicMock(),
        config={},
        transformations=MagicMock(),
        parameters={},
    )

    assert stream.state_checkpoint_interval is None
