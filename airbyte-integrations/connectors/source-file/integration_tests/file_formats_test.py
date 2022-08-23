#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from pathlib import Path
from unittest.mock import patch

import pytest
from airbyte_cdk import AirbyteLogger
from source_file import SourceFile
from source_file.client import Client

SAMPLE_DIRECTORY = Path(__file__).resolve().parent.joinpath("sample_files/formats")


def check_read(config, expected_columns=10, expected_rows=42):
    client = Client(**config)
    rows = list(client.read())
    assert len(rows) == expected_rows
    assert len(rows[0]) == expected_columns


@pytest.mark.parametrize(
    "file_format, extension, expected_columns, expected_rows, filename",
    [
        ("csv", "csv", 8, 5000, "demo"),
        ("json", "json", 2, 1, "demo"),
        ("jsonl", "jsonl", 2, 10, "jsonl_nested"),
        ("jsonl", "jsonl", 2, 6492, "jsonl"),
        ("excel", "xls", 8, 50, "demo"),
        ("excel", "xlsx", 8, 50, "demo"),
        ("feather", "feather", 9, 3, "demo"),
        ("parquet", "parquet", 9, 3, "demo"),
        ("yaml", "yaml", 8, 3, "demo"),
    ],
)
def test_local_file_read(file_format, extension, expected_columns, expected_rows, filename):
    file_directory = SAMPLE_DIRECTORY.joinpath(file_format)
    file_path = str(file_directory.joinpath(f"{filename}.{extension}"))
    configs = {"dataset_name": "test", "format": file_format, "url": file_path, "provider": {"storage": "local"}}
    check_read(configs, expected_columns, expected_rows)


def run_load_dataframes(config, expected_columns=10, expected_rows=42):
    df_list = SourceFile.load_dataframes(config=config, logger=AirbyteLogger(), skip_data=False)
    assert len(df_list) == 1  # Properly load 1 DataFrame
    df = df_list[0]
    assert len(df.columns) == expected_columns  # DataFrame should have 10 columns
    assert len(df.index) == expected_rows  # DataFrame should have 42 rows of data
    return df


def run_load_nested_json_schema(config, expected_columns=10, expected_rows=42):
    data_list = SourceFile.load_nested_json(config, logger=AirbyteLogger())
    assert len(data_list) == 1  # Properly load data
    df = data_list[0]
    assert len(df) == expected_rows  # DataFrame should have 42 items
    return df


# https://github.com/airbytehq/alpha-beta-issues/issues/174
# this is to ensure we make all conditions under which the bug is reproduced, i.e.
# - chunk size < file size
# - column type in the last chunk is not `string`
@patch("source_file.client.Client.CSV_CHUNK_SIZE", 1)
def test_csv_schema():
    source = SourceFile()
    file_path = str(SAMPLE_DIRECTORY.parent.joinpath("discover.csv"))
    config = {"dataset_name": "test", "format": "csv", "url": file_path, "provider": {"storage": "local"}}
    catalog = source.discover(logger=AirbyteLogger(), config=config).dict()
    assert len(catalog["streams"]) == 1
    schema = catalog["streams"][0]["json_schema"]
    assert schema == {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {
            "Address": {"type": ["string", "null"]},
            "City": {"type": ["string", "null"]},
            "First Name": {"type": ["string", "null"]},
            "Last Name": {"type": ["string", "null"]},
            "State": {"type": ["string", "null"]},
            "zip_code": {"type": ["string", "null"]},
        },
        "type": "object",
    }
