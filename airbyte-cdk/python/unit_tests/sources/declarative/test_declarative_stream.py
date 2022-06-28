#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream


def test():
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
    retriever.get_state.return_value = state
    retriever.read_records.return_value = records
    retriever.stream_slices.return_value = stream_slices
    retriever.state_checkpoint_interval = checkpoint_interval

    stream = DeclarativeStream(
        name=name,
        primary_key=primary_key,
        cursor_field=cursor_field,
        schema_loader=schema_loader,
        retriever=retriever,
    )

    assert stream.name == name
    assert stream.get_json_schema() == json_schema
    assert stream.state == state
    assert stream.read_records(SyncMode.full_refresh, cursor_field, None, None) == records
    assert stream.primary_key == primary_key
    assert stream.cursor_field == cursor_field
    assert stream.stream_slices(sync_mode=SyncMode.incremental, cursor_field=cursor_field, stream_state=None) == stream_slices
