#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, AirbyteTraceMessage, Level, SyncMode, TraceType, Type
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.types import StreamSlice

SLICE_NOT_CONSIDERED_FOR_EQUALITY = {}

_name = "stream"
_primary_key = "pk"
_cursor_field = "created_at"
_json_schema = {"name": {"type": "string"}}


def test_declarative_stream():
    schema_loader = _schema_loader()

    state = MagicMock()
    records = [
        {"pk": 1234, "field": "value"},
        {"pk": 4567, "field": "different_value"},
        AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="This is a log  message")),
        AirbyteMessage(type=Type.TRACE, trace=AirbyteTraceMessage(type=TraceType.ERROR, emitted_at=12345)),
    ]
    stream_slices = [
        StreamSlice(partition={}, cursor_slice={"date": "2021-01-01"}),
        StreamSlice(partition={}, cursor_slice={"date": "2021-01-02"}),
        StreamSlice(partition={}, cursor_slice={"date": "2021-01-03"}),
    ]

    retriever = MagicMock()
    retriever.state = state
    retriever.read_records.return_value = records
    retriever.stream_slices.return_value = stream_slices

    config = {"api_key": "open_sesame"}

    stream = DeclarativeStream(
        name=_name,
        primary_key=_primary_key,
        stream_cursor_field="{{ parameters['cursor_field'] }}",
        schema_loader=schema_loader,
        retriever=retriever,
        config=config,
        parameters={"cursor_field": "created_at"},
    )

    assert stream.name == _name
    assert stream.get_json_schema() == _json_schema
    assert stream.state == state
    input_slice = stream_slices[0]
    assert list(stream.read_records(SyncMode.full_refresh, _cursor_field, input_slice, state)) == records
    assert stream.primary_key == _primary_key
    assert stream.cursor_field == _cursor_field
    assert stream.stream_slices(sync_mode=SyncMode.incremental, cursor_field=_cursor_field, stream_state=None) == stream_slices


def test_declarative_stream_using_empty_slice():
    """
    Tests that a declarative_stream
    """
    schema_loader = _schema_loader()

    records = [
        {"pk": 1234, "field": "value"},
        {"pk": 4567, "field": "different_value"},
        AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="This is a log  message")),
        AirbyteMessage(type=Type.TRACE, trace=AirbyteTraceMessage(type=TraceType.ERROR, emitted_at=12345)),
    ]

    retriever = MagicMock()
    retriever.read_records.return_value = records

    config = {"api_key": "open_sesame"}

    stream = DeclarativeStream(
        name=_name,
        primary_key=_primary_key,
        stream_cursor_field="{{ parameters['cursor_field'] }}",
        schema_loader=schema_loader,
        retriever=retriever,
        config=config,
        parameters={"cursor_field": "created_at"},
    )

    assert stream.name == _name
    assert stream.get_json_schema() == _json_schema
    assert list(stream.read_records(SyncMode.full_refresh, _cursor_field, {})) == records


def test_read_records_raises_exception_if_stream_slice_is_not_per_partition_stream_slice():
    schema_loader = _schema_loader()

    retriever = MagicMock()
    retriever.state = MagicMock()
    retriever.read_records.return_value = []
    stream_slice = {"date": "2021-01-01"}
    retriever.stream_slices.return_value = [stream_slice]

    stream = DeclarativeStream(
        name=_name,
        primary_key=_primary_key,
        stream_cursor_field="{{ parameters['cursor_field'] }}",
        schema_loader=schema_loader,
        retriever=retriever,
        config={},
        parameters={"cursor_field": "created_at"},
    )

    with pytest.raises(ValueError):
        list(stream.read_records(SyncMode.full_refresh, _cursor_field, stream_slice, MagicMock()))


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


def test_state_migrations():
    intermediate_state = {"another_key", "another_value"}
    final_state = {"yet_another_key", "yet_another_value"}
    first_state_migration = MagicMock()
    first_state_migration.should_migrate.return_value = True
    first_state_migration.migrate.return_value = intermediate_state
    second_state_migration = MagicMock()
    second_state_migration.should_migrate.return_value = True
    second_state_migration.migrate.return_value = final_state

    stream = DeclarativeStream(
        name="any name",
        primary_key="any primary key",
        stream_cursor_field="{{ parameters['cursor_field'] }}",
        schema_loader=MagicMock(),
        retriever=MagicMock(),
        state_migrations=[first_state_migration, second_state_migration],
        config={},
        parameters={},
    )

    input_state = {"a_key": "a_value"}

    stream.state = input_state
    assert stream.state == final_state
    first_state_migration.should_migrate.assert_called_once_with(input_state)
    first_state_migration.migrate.assert_called_once_with(input_state)
    second_state_migration.should_migrate.assert_called_once_with(intermediate_state)
    second_state_migration.migrate.assert_called_once_with(intermediate_state)


def test_no_state_migration_is_applied_if_the_state_should_not_be_migrated():
    state_migration = MagicMock()
    state_migration.should_migrate.return_value = False

    stream = DeclarativeStream(
        name="any name",
        primary_key="any primary key",
        stream_cursor_field="{{ parameters['cursor_field'] }}",
        schema_loader=MagicMock(),
        retriever=MagicMock(),
        state_migrations=[state_migration],
        config={},
        parameters={},
    )

    input_state = {"a_key": "a_value"}

    stream.state = input_state
    assert stream.state == input_state
    state_migration.should_migrate.assert_called_once_with(input_state)
    assert not state_migration.migrate.called


@pytest.mark.parametrize(
    "use_cursor, expected_supports_checkpointing",
    [
        pytest.param(True, True, id="test_retriever_has_cursor"),
        pytest.param(False, False, id="test_retriever_has_cursor"),
    ],
)
def test_is_resumable(use_cursor, expected_supports_checkpointing):
    schema_loader = _schema_loader()

    state = MagicMock()

    retriever = MagicMock()
    retriever.state = state
    retriever.cursor = MagicMock() if use_cursor else None

    config = {"api_key": "open_sesame"}

    stream = DeclarativeStream(
        name=_name,
        primary_key=_primary_key,
        stream_cursor_field="{{ parameters['cursor_field'] }}",
        schema_loader=schema_loader,
        retriever=retriever,
        config=config,
        parameters={"cursor_field": "created_at"},
    )

    assert stream.is_resumable == expected_supports_checkpointing


def _schema_loader():
    schema_loader = MagicMock()
    schema_loader.get_json_schema.return_value = _json_schema
    return schema_loader
