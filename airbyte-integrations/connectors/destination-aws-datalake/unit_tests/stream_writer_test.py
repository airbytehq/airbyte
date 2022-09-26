#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import pandas as pd

from datetime import datetime
from typing import Any, Mapping, Dict

from destination_aws_datalake import DestinationAwsDatalake
from destination_aws_datalake.aws import AwsHandler
from destination_aws_datalake.stream_writer import StreamWriter
from destination_aws_datalake.config_reader import ConnectorConfig
from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)


def get_config() -> Mapping[str, Any]:
    with open("unit_tests/fixtures/config.json", "r") as f:
        return json.loads(f.read())


def get_configured_stream():
    stream_name = "append_stream"
    stream_schema = {
        "type": "object",
        "properties": {
            "string_col": {"type": "str"},
            "int_col": {"type": "integer"},
            "datetime_col": {"type": "string", "format": "date-time"},
            "date_col": {"type": "string", "format": "date"},
        },
    }

    return ConfiguredAirbyteStream(
        stream=AirbyteStream(name=stream_name, json_schema=stream_schema, default_cursor_field=["datetime_col"]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
        cursor_field=["datetime_col"],
    )


def get_writer(config: Dict[str, Any]):
    connector_config = ConnectorConfig(**config)
    aws_handler = AwsHandler(connector_config, DestinationAwsDatalake())
    return StreamWriter(aws_handler, connector_config, get_configured_stream())


def test_get_path():
    writer = get_writer(get_config())
    assert writer._get_path() == f"s3://datalake-bucket/test/append_stream/"


def test_get_path_prefix():
    config = get_config()
    config["bucket_prefix"] = "prefix"
    writer = get_writer(config)
    assert writer._get_path() == f"s3://datalake-bucket/prefix/test/append_stream/"


def test_get_date_columns():
    writer = get_writer(get_config())
    assert writer._get_date_columns() == ["datetime_col", "date_col"]


def test_append_messsage():
    writer = get_writer(get_config())
    message = {"string_col": "test", "int_col": 1, "datetime_col": "2021-01-01T00:00:00Z", "date_col": "2021-01-01"}
    writer.append_message(message)
    assert len(writer._messages) == 1
    assert writer._messages[0] == message


def test_get_cursor_field():
    writer = get_writer(get_config())
    assert writer._cursor_fields == ["datetime_col"]


def test_add_partition_column():
    tests= {
        "NO PARTITIONING": [],
        "DATE": ["datetime_col_date"],
        "MONTH": ["datetime_col_month"],
        "YEAR": ["datetime_col_year"],
        "DAY": ["datetime_col_day"],
        "YEAR/MONTH/DAY": ["datetime_col_year", "datetime_col_month", "datetime_col_day"],
    }

    for partitioning, expected_columns in tests.items():
        config = get_config()
        config["partitioning"] = partitioning

        writer = get_writer(config)
        df = pd.DataFrame(
            {
                "datetime_col": [datetime.now()],
            }
        )
        assert writer._add_partition_column("datetime_col", df) == expected_columns
        assert all([col in df.columns for col in expected_columns])

