#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest import mock
from unittest.mock import MagicMock, call

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.transformations import RecordTransformation


def test_declarative_stream():
    name = "stream"
    primary_key = "pk"
    cursor_field = ["created_at"]

    schema_loader = MagicMock()
    json_schema = {"name": {"type": "string"}}
    schema_loader.get_json_schema.return_value = json_schema

    state = MagicMock()
    records = [{"pk": 1234, "field": "value"}, {"pk": 4567, "field": "different_value"}]
    stream_slices = [{"date": "2021-01-01"}, {"date": "2021-01-02"}, {"date": "2021-01-03"}]
    checkpoint_interval = 1000

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
        stream_cursor_field=cursor_field,
        schema_loader=schema_loader,
        retriever=retriever,
        config=config,
        transformations=transformations,
        checkpoint_interval=checkpoint_interval,
        options={},
    )

    assert stream.name == name
    assert stream.get_json_schema() == json_schema
    assert stream.state == state
    input_slice = stream_slices[0]
    assert list(stream.read_records(SyncMode.full_refresh, cursor_field, input_slice, state)) == records
    assert stream.primary_key == primary_key
    assert stream.cursor_field == cursor_field
    assert stream.stream_slices(sync_mode=SyncMode.incremental, cursor_field=cursor_field, stream_state=None) == stream_slices
    assert stream.state_checkpoint_interval == checkpoint_interval
    for transformation in transformations:
        assert len(transformation.transform.call_args_list) == len(records)
        expected_calls = [call(record, config=config, stream_slice=input_slice, stream_state=state) for record in records]
        transformation.transform.assert_has_calls(expected_calls, any_order=False)
