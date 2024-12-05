# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import tempfile
from unittest.mock import Mock, patch

import pytest
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type
from destination_motherduck.destination import CONFIG_DEFAULT_SCHEMA, DestinationMotherDuck, validated_sql_name


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
