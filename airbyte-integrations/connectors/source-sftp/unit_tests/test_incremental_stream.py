from datetime import datetime
from unittest.mock import patch

import pytest
from airbyte_cdk.models.airbyte_protocol import SyncMode


@pytest.mark.parametrize(
    "current_stream_state, latest_record, expected",
    [
        (
            {"_ab_file_last_modified": "2020-01-01T00:00:00+00:00"},
            {"name": "Ann", "age": 20, "_ab_file_last_modified": "2020-05-25T01:02:03+05:00"},
            {"_ab_file_last_modified": "2020-05-25T01:02:03+05:00"},
        ),
        (
            None,
            {"name": "Bob", "age": 50, "email": "ann@mail.com", "_ab_file_last_modified": "2000-02-07T01:02:03-05:00"},
            {"_ab_file_last_modified": "2000-02-07T01:02:03-05:00"},
        ),
        (
            {"_ab_file_last_modified": "2020-01-01T00:00:00.123"},
            {"name": "Bob", "age": 50, "email": "ann@mail.com"},
            {"_ab_file_last_modified": "2020-01-01T00:00:00+00:00"},
        ),
        (
            None,
            None,
            {"_ab_file_last_modified": "2000-01-01T00:00:00+00:00"},
        ),
    ],
)
def test_get_updated_state(current_stream_state, latest_record, expected, incremental_stream):
    state = incremental_stream.get_updated_state(current_stream_state, latest_record)
    assert state == expected


@pytest.mark.parametrize(
    "file_infos, expected",
    [
        (
            [
                {"filepath": "a.csv", "last_modified": datetime(2021, 1, 1)},
                {"filepath": "b.csv", "last_modified": datetime(2021, 1, 1)},
                {"filepath": "c.csv", "last_modified": datetime(2021, 1, 3)},
                {"filepath": "d.csv", "last_modified": datetime(2021, 1, 3)},
                {"filepath": "e.csv", "last_modified": datetime(2023, 2, 3)},
            ],
            [
                [
                    {"filepath": "a.csv", "last_modified": datetime(2021, 1, 1)},
                    {"filepath": "b.csv", "last_modified": datetime(2021, 1, 1)},
                ],
                [
                    {"filepath": "c.csv", "last_modified": datetime(2021, 1, 3)},
                    {"filepath": "d.csv", "last_modified": datetime(2021, 1, 3)},
                ],
                [{"filepath": "e.csv", "last_modified": datetime(2023, 2, 3)}],
                None
            ],
        )
    ],
)
@patch("source_sftp.client.Client.close")
@patch("source_sftp.client.Client.get_files")
def test_stream_slices(mocked_get_files, mocked_close, file_infos, expected, incremental_stream):
    mocked_get_files.return_value = file_infos
    slices = []
    for slice in incremental_stream.stream_slices(sync_mode=SyncMode.incremental):
        slices.append(slice)
    assert slices == expected
