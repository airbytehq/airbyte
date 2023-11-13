#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, AirbyteTraceMessage, Level, SyncMode, TraceType, Type
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream

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

    config = {"api_key": "open_sesame"}

    stream = DeclarativeStream(
        name=name,
        primary_key=primary_key,
        stream_cursor_field="{{ parameters['cursor_field'] }}",
        schema_loader=schema_loader,
        retriever=retriever,
        config=config,
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


def test_state_checkpoint_interval():
    stream = DeclarativeStream(
        name="any name",
        primary_key="any primary key",
        stream_cursor_field="{{ parameters['cursor_field'] }}",
        schema_loader=MagicMock(),
        retriever=MagicMock(),
        config={},
        parameters={},
    )

    assert stream.state_checkpoint_interval is None
