#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, MutableMapping

import pytest
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from source_s3.v4.cursor import Cursor


@pytest.mark.parametrize(
    "input_state, expected_state",
    [
        pytest.param({}, {"history": {}, "_ab_source_file_last_modified": None}, id="empty-history"),
        pytest.param(
            {"history": {"2023-08-01": ["file1.txt"]}, "_ab_source_file_last_modified": "2023-08-01T00:00:00Z"},
            {
                "history": {
                    "file1.txt": "2023-08-01T00:00:00.000000Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T00:00:00.000000Z_file1.txt",
            },
            id="single-date-single-file",
        ),
        pytest.param(
            {"history": {"2023-08-01": ["file1.txt", "file2.txt"]}, "_ab_source_file_last_modified": "2023-08-01T00:00:00Z"},
            {
                "history": {
                    "file1.txt": "2023-08-01T00:00:00.000000Z",
                    "file2.txt": "2023-08-01T00:00:00.000000Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T00:00:00.000000Z_file2.txt",
            },
            id="single-date-multiple-files",
        ),
        pytest.param(
            {
                "history": {
                    "2023-08-01": ["file1.txt", "file2.txt"],
                    "2023-07-31": ["file1.txt", "file3.txt"],
                    "2023-07-30": ["file3.txt"],
                },
                "_ab_source_file_last_modified": "2023-08-01T00:00:00Z",
            },
            {
                "history": {
                    "file1.txt": "2023-08-01T00:00:00.000000Z",
                    "file2.txt": "2023-08-01T00:00:00.000000Z",
                    "file3.txt": "2023-07-31T00:00:00.000000Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T00:00:00.000000Z_file2.txt",
            },
            id="multiple-dates-multiple-files",
        ),
    ],
)
def test_set_initial_state_with_v3_state(input_state: MutableMapping[str, Any], expected_state: MutableMapping[str, Any]) -> None:
    cursor = Cursor(stream_config=FileBasedStreamConfig(file_type="csv", name="test", validation_policy="Emit Records"))
    cursor.set_initial_state(input_state)
    assert cursor.get_state() == expected_state
