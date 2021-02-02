"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from pathlib import Path

import pytest
from base_python import AirbyteLogger
from source_file import SourceFile
from source_file.client import Client

SAMPLE_DIRECTORY = Path(__file__).resolve().parent.joinpath("sample_files/formats")


def check_read(config, expected_columns=10, expected_rows=42):
    client = Client(**config)
    rows = list(client.read())
    assert len(rows) == expected_rows
    assert len(rows[0]) == expected_columns


@pytest.mark.parametrize(
    "file_format, extension, expected_columns, expected_rows",
    [
        ("csv", "csv", 8, 5000),
        ("json", "json", 2, 1),
        ("excel", "xls", 8, 50),
        ("excel", "xlsx", 8, 50),
        ("feather", "feather", 9, 3),
        ("parquet", "parquet", 9, 3),
    ],
)
def test_local_file_read(file_format, extension, expected_columns, expected_rows):
    file_directory = SAMPLE_DIRECTORY.joinpath(file_format)
    file_path = str(file_directory.joinpath(f"demo.{extension}"))
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
