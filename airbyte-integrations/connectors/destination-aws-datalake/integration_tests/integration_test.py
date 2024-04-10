#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from datetime import datetime
from typing import Any, Dict, Mapping

import awswrangler as wr
import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    StreamDescriptor,
    SyncMode,
    Type,
)
from destination_aws_datalake import DestinationAwsDatalake
from destination_aws_datalake.aws import AwsHandler
from destination_aws_datalake.config_reader import ConnectorConfig

logger = logging.getLogger("airbyte")


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="invalid_region_config")
def invalid_region_config() -> Mapping[str, Any]:
    with open("integration_tests/invalid_region_config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="invalid_account_config")
def invalid_account_config() -> Mapping[str, Any]:
    with open("integration_tests/invalid_account_config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {
        "type": "object",
        "properties": {
            "string_col": {"type": "str"},
            "int_col": {"type": "integer"},
            "date_col": {"type": "string", "format": "date-time"},
        },
    }

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="append_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="overwrite_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[append_stream, overwrite_stream])


def test_check_valid_config(config: Mapping):
    outcome = DestinationAwsDatalake().check(logger, config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_aws_region_config(invalid_region_config: Mapping):
    outcome = DestinationAwsDatalake().check(logger, invalid_region_config)
    assert outcome.status == Status.FAILED


def test_check_invalid_aws_account_config(invalid_account_config: Mapping):
    outcome = DestinationAwsDatalake().check(logger, invalid_account_config)
    assert outcome.status == Status.FAILED


def _state(stream: str, data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(
        type=AirbyteStateType.STREAM,
        stream=AirbyteStreamState(
            stream_state=data,
            stream_descriptor=StreamDescriptor(name=stream, namespace=None)
        )
    ))


def _record(stream: str, str_value: str, int_value: int, date_value: datetime) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(stream=stream, data={"str_col": str_value, "int_col": int_value, "date_col": date_value}, emitted_at=0),
    )


def test_write(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    """
    This test verifies that:
        1. writing a stream in "overwrite" mode overwrites any existing data for that stream
        2. writing a stream in "append" mode appends new records without deleting the old ones
        3. The correct state message is output by the connector at the end of the sync
    """
    append_stream, overwrite_stream = configured_catalog.streams[0].stream.name, configured_catalog.streams[1].stream.name

    destination = DestinationAwsDatalake()

    connector_config = ConnectorConfig(**config)
    aws_handler = AwsHandler(connector_config, destination)

    database = connector_config.lakeformation_database_name

    # make sure we start with empty tables
    for tbl in [append_stream, overwrite_stream]:
        aws_handler.reset_table(database, tbl)

    first_state_message = _state(append_stream, {"state": "1"})

    first_record_chunk = [_record(append_stream, str(i), i, datetime.now()) for i in range(5)] + [
        _record(overwrite_stream, str(i), i, datetime.now()) for i in range(5)
    ]

    second_state_message = _state(append_stream, {"state": "2"})
    second_record_chunk = [_record(append_stream, str(i), i, datetime.now()) for i in range(5, 10)] + [
        _record(overwrite_stream, str(i), i, datetime.now()) for i in range(5, 10)
    ]

    expected_states = [first_state_message, second_state_message]
    output_states = list(
        destination.write(
            config, configured_catalog, [*first_record_chunk, first_state_message, *second_record_chunk, second_state_message]
        )
    )
    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"

    # Check if table was created
    for tbl in [append_stream, overwrite_stream]:
        table = wr.catalog.table(database=database, table=tbl, boto3_session=aws_handler._session)
        expected_types = {"string_col": "string", "int_col": "bigint", "date_col": "timestamp"}

        # Check table format
        for col in table.to_dict("records"):
            assert col["Column Name"] in ["string_col", "int_col", "date_col"]
            assert col["Type"] == expected_types[col["Column Name"]]

        # Check table data
        # cannot use wr.lakeformation.read_sql_query because of this issue: https://github.com/aws/aws-sdk-pandas/issues/2007
        df = wr.athena.read_sql_query(f"SELECT * FROM {tbl}", database=database, boto3_session=aws_handler._session)
        assert len(df) == 10

        # Reset table
        aws_handler.reset_table(database, tbl)
