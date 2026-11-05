#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

import pytest
from source_file.client import Client


SAMPLE_FORMATS_DIRECTORY = Path(__file__).resolve().parent.parent / "integration_tests" / "sample_files" / "formats"


@pytest.mark.parametrize(
    "file_format, file_name, expected_columns, expected_rows",
    [
        ("parquet", "demo.parquet", 9, 3),
        ("feather", "demo.feather", 9, 3),
        ("orc", "demo.orc", 12, 2),
        ("excel", "demo.xlsx", 8, 50),
    ],
)
def test_read_local_binary_formats(file_format, file_name, expected_columns, expected_rows):
    """Binary formats go through pyarrow/fastparquet/numpy, which must load on the base image's Python version."""
    config = {
        "dataset_name": "test",
        "format": file_format,
        "url": str(SAMPLE_FORMATS_DIRECTORY / file_format / file_name),
        "provider": {"storage": "local"},
    }

    records = list(Client(**config).read())

    assert len(records) == expected_rows
    assert all(len(record) == expected_columns for record in records)
    json.dumps(records, default=str)
