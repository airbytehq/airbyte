# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import tempfile
from datetime import datetime
from typing import Dict
from unittest.mock import Mock, patch

import pytest
from destination_motherduck.destination import CONFIG_DEFAULT_SCHEMA, DestinationMotherDuck, validated_sql_name

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)


def test_validated_sql_name() -> None:
    assert validated_sql_name("valid_name") == "valid_name"
    with pytest.raises(ValueError):
        validated_sql_name("invalid-name")


@patch("os.makedirs")
@patch("sqlalchemy.create_engine")
def test_check(mock_makedirs, mock_create_engine, monkeypatch) -> None:
    # Mocked return from fetchall():
    mock_result = Mock()
    mock_result.fetchall.return_value = [(1,)]

    # Mocked connection context manager:
    mock_connection = Mock()
    mock_connection.execute.return_value = mock_result
    mock_connection.__enter__ = Mock(return_value=mock_connection)
    mock_connection.__exit__ = Mock(return_value=None)

    # Mocked engine, to return the mocked connection:
    mock_engine = Mock()
    mock_engine.begin.return_value = mock_connection
    mock_create_engine.return_value = mock_engine

    monkeypatch.setattr(DestinationMotherDuck, "_get_destination_path", lambda _, x: x)
    logger = Mock()
    temp_dir = tempfile.mkdtemp()
    config = {"destination_path": f"{temp_dir}/testdb.db"}
    destination = DestinationMotherDuck()
    result = destination.check(logger, config)
    assert result.status == Status.SUCCEEDED


@patch("destination_motherduck.processors.duckdb.DuckDBSqlProcessor._execute_sql")
@patch("os.makedirs")
def test_check_failure(mock_makedirs, mock_execute_sql, monkeypatch) -> None:
    mock_execute_sql.side_effect = Exception("Test exception")
    monkeypatch.setattr(DestinationMotherDuck, "_get_destination_path", lambda _, x: x)
    logger = Mock()
    temp_dir = tempfile.mkdtemp()
    config = {"destination_path": f"{temp_dir}/testdb.db"}
    destination = DestinationMotherDuck()
    result = destination.check(logger, config)
    assert result.status == Status.FAILED
    assert "Test exception" in result.message


@patch("os.makedirs")
@patch("sqlalchemy.create_engine")
def test_write(mock_makedirs, mock_create_engine, monkeypatch) -> None:
    mock_connection = Mock()
    mock_result = Mock()
    mock_result.fetchall.return_value = []
    mock_connection.execute.return_value = mock_result
    mock_connection.__enter__ = Mock(return_value=mock_connection)
    mock_connection.__exit__ = Mock(return_value=None)

    mock_engine = Mock()
    mock_engine.begin.return_value = mock_connection
    mock_create_engine.return_value = mock_engine

    monkeypatch.setattr(DestinationMotherDuck, "_get_destination_path", lambda _, x: x)
    temp_dir = tempfile.mkdtemp()
    config = {"destination_path": f"{temp_dir}/testdb.db", "schema": CONFIG_DEFAULT_SCHEMA}
    catalog = ConfiguredAirbyteCatalog(streams=[])
    messages = [AirbyteMessage(type=Type.STATE, record=None, state=AirbyteStateMessage(data={"state": "1"}))]
    destination = DestinationMotherDuck()
    result = list(destination.write(config, catalog, messages))
    assert len(result) == 1
    assert result[0].type == Type.STATE


def test_null_primary_key_handling(monkeypatch) -> None:
    """Integration test that records with null primary key values can be processed through the connector."""

    monkeypatch.setattr(DestinationMotherDuck, "_get_destination_path", lambda _, x: x)

    temp_dir = tempfile.mkdtemp()
    config = {"destination_path": f"{temp_dir}/test_null_pk.duckdb", "schema": "test_schema"}
    test_table_name = "test_null_pk_table"
    test_schema_name = "test_schema"

    table_schema = {
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
            "name": {"type": ["null", "string"]},
        },
    }

    configured_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=test_table_name,
            json_schema=table_schema,
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append_dedup,
        primary_key=[["id"]],
    )

    configured_catalog = ConfiguredAirbyteCatalog(streams=[configured_stream])

    messages = [
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream=test_table_name,
                data={"id": None, "name": "record_with_null_pk_1"},
                emitted_at=int(datetime.now().timestamp()) * 1000,
            ),
        ),
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream=test_table_name,
                data={"id": "valid_id", "name": "record_with_valid_pk"},
                emitted_at=int(datetime.now().timestamp()) * 1000,
            ),
        ),
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream=test_table_name,
                data={"id": None, "name": "record_with_null_pk_2"},
                emitted_at=int(datetime.now().timestamp()) * 1000,
            ),
        ),
        AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"state": "1"})),
    ]

    destination = DestinationMotherDuck()
    result = list(destination.write(config, configured_catalog, messages))

    assert len(result) == 1
    assert result[0].type == Type.STATE

    processor = destination._get_sql_processor(
        configured_catalog=configured_catalog,
        schema_name=test_schema_name,
        db_path=config.get("destination_path", ":memory:"),
    )

    sql_result = processor._execute_sql(f"SELECT id, name FROM {test_schema_name}.{test_table_name} ORDER BY name")

    assert len(sql_result) == 2, f"Expected 2 records after deduplication, got {len(sql_result)}"

    ids = [row[0] for row in sql_result]
    names = [row[1] for row in sql_result]

    assert "valid_id" in ids, "Expected to find record with valid_id"
    assert None in ids, "Expected to find record with NULL id"
    assert "record_with_valid_pk" in names, "Expected to find record with valid primary key"
    assert "record_with_null_pk_2" in names, "Expected to find the latest null primary key record (record_with_null_pk_2)"
