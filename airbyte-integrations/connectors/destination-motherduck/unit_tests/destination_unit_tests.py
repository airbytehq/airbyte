# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from destination_motherduck.destination import CONFIG_DEFAULT_SCHEMA, DestinationMotherDuck, validated_sql_name

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
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


@patch("duckdb.connect")
@patch("os.makedirs")
def test_check(mock_connect, mock_makedirs) -> None:
    mock_connect.return_value.execute.return_value = True
    logger = Mock()
    temp_dir = tempfile.mkdtemp()
    config = {"destination_path": "/local/test"}
    # config = {"destination_path": f"{temp_dir}/testdb.db"}
    destination = DestinationMotherDuck()
    result = destination.check(logger, config)
    assert result.status == Status.SUCCEEDED


@patch("duckdb.connect")
@patch("os.makedirs")
def test_check_failure(mock_connect, mock_makedirs) -> None:
    mock_connect.side_effect = Exception("Test exception")
    logger = Mock()
    config = {"destination_path": "/local/test"}
    destination = DestinationMotherDuck()
    result = destination.check(logger, config)
    assert result.status == Status.FAILED
    assert "Test exception" in result.message


@patch("duckdb.connect")
@patch("os.makedirs")
def test_write(mock_connect, mock_makedirs) -> None:
    mock_connect.return_value.execute.return_value = True
    config = {"destination_path": "/local/test", "schema": CONFIG_DEFAULT_SCHEMA}
    catalog = ConfiguredAirbyteCatalog(streams=[])
    messages = [AirbyteMessage(type=Type.STATE, record=None)]
    destination = DestinationMotherDuck()
    result = list(destination.write(config, catalog, messages))
    assert len(result) == 1
    assert result[0].type == Type.STATE


def test_null_primary_key_handling() -> None:
    """Test that records with null primary key values can be processed."""
    import duckdb

    conn = duckdb.connect(":memory:")

    try:
        conn.execute("""
            CREATE TABLE test_stream (
                id VARCHAR,
                name VARCHAR,
                _airbyte_extracted_at TIMESTAMP
            )
        """)

        conn.execute("""
            INSERT INTO test_stream (id, name, _airbyte_extracted_at)
            VALUES (NULL, 'record1', CURRENT_TIMESTAMP)
        """)

        conn.execute("""
            INSERT INTO test_stream (id, name, _airbyte_extracted_at)
            VALUES ('valid_id', 'record2', CURRENT_TIMESTAMP)
        """)

        conn.execute("""
            INSERT INTO test_stream (id, name, _airbyte_extracted_at)
            VALUES (NULL, 'record3', CURRENT_TIMESTAMP)
        """)

        result = conn.execute("SELECT COUNT(*) FROM test_stream").fetchone()
        assert result[0] == 3, f"Expected 3 records, got {result[0]}"

        dedup_result = conn.execute("""
            SELECT * FROM test_stream
            QUALIFY row_number() OVER (PARTITION BY id ORDER BY _airbyte_extracted_at DESC) = 1
            ORDER BY _airbyte_extracted_at
        """).fetchall()

        assert len(dedup_result) == 2, f"Expected 2 records after deduplication, got {len(dedup_result)}"

        ids = [row[0] for row in dedup_result]
        assert "valid_id" in ids, "Expected to find record with valid_id"
        assert None in ids, "Expected to find record with NULL id"

        print("Successfully inserted and deduplicated records with null primary keys")

    finally:
        conn.close()
