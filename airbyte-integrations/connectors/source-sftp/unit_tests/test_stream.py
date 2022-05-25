from unittest.mock import MagicMock, patch
import pytest
import pytz
from datetime import datetime

from airbyte_cdk.models.airbyte_protocol import SyncMode
from source_sftp.stream import SFTPStream
from source_sftp.client import get_client


@pytest.mark.parametrize(
    "dttm, expected",
    [
        ("2020-01-01T00:00:00", datetime(2020, 1, 1, tzinfo=pytz.UTC)),
        ("2021-12-31T23:59:59+00:00", datetime(2021, 12, 31, 23, 59, 59, tzinfo=pytz.UTC)),
        ("2021-12-31T23:59:59.123+00:00", datetime(2021, 12, 31, 23, 59, 59, microsecond=123000, tzinfo=pytz.UTC)),
        ("2021-12-31T23:59:59.123456+00:00", datetime(2021, 12, 31, 23, 59, 59, microsecond=123456, tzinfo=pytz.UTC)),
    ],
)
def test_parse_dttm(dttm, expected):
    result = SFTPStream.parse_dttm(dttm)
    assert result == expected


@pytest.mark.parametrize(
    "dttm, expected",
    [
        (datetime(2020, 1, 1, tzinfo=pytz.UTC), "2020-01-01T00:00:00+00:00"),
        (datetime(2021, 12, 31, 23, 59, 59, tzinfo=pytz.UTC), "2021-12-31T23:59:59+00:00"),
        (datetime(2021, 12, 31, 23, 59, 59, microsecond=123000, tzinfo=pytz.UTC), "2021-12-31T23:59:59+00:00"),
    ],
)
def test_format_dttm(dttm, expected):
    result = SFTPStream.format_dttm(dttm)
    assert result == expected


@patch("source_sftp.client.Client.get_file_properties")
@patch("source_sftp.client.Client.get_files")
def test_get_json_schema(mocked_get_files, mocked_get_file_properties, client_config):
    mocked_get_files.return_value = [{"filepath": "", "last_modified": None}]
    mocked_get_file_properties.return_value = {
        "number_col": {"type": ["number", "null"]},
        "str_col": {"type": ["string", "null"]},
        "nan_col": {"type": ["string", "null"]},
    }
    expected = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "number_col": {"type": ["number", "null"]},
            "str_col": {"type": ["string", "null"]},
            "nan_col": {"type": ["string", "null"]},
            SFTPStream.ab_file_path_column: {"type": ["string", "null"]},
            SFTPStream.ab_last_modified_column: {
                "type": ["string", "null"],
                "format": "date-time",
                "airbyte_type": "timestamp_with_timezone",
            },
        },
    }
    client = get_client(client_config)
    stream = SFTPStream(client, "dataset")
    json_schema = stream.get_json_schema()
    assert json_schema == expected


@pytest.mark.parametrize(
    "file_infos, expected",
    [
        (
            [
                {"filepath": "a.csv", "last_modified": datetime(2021, 1, 1)},
                {"filepath": "b.csv", "last_modified": datetime(2021, 1, 2)},
                {"filepath": "c.csv", "last_modified": datetime(2021, 1, 3)},
            ],
            [
                [{"filepath": "a.csv", "last_modified": datetime(2021, 1, 1)}],
                [{"filepath": "b.csv", "last_modified": datetime(2021, 1, 2)}],
                [{"filepath": "c.csv", "last_modified": datetime(2021, 1, 3)}],
            ],
        )
    ],
)
@patch("source_sftp.client.Client.close")
@patch("source_sftp.client.Client.get_files")
def test_stream_slices(mocked_get_files, mocked_close, file_infos, expected, stream):
    mocked_get_files.return_value = file_infos
    all_slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))
    assert all_slices == expected


@patch("source_sftp.client.Client.close")
@patch("source_sftp.client.Client.get_files")
def test_stream_slices_with_no_file(mocked_get_files, mocked_close, stream):
    mocked_get_files.return_values = []
    all_slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))
    assert all_slices == []


@pytest.mark.parametrize(
    "records, stream_slice, expected",
    [
        (
            [
                {"a": 1, "b": "text", "c": datetime(2021, 1, 1)},
                {"a": 2, "b": "text2", "c": datetime(2021, 1, 2)},
            ],
            [{"filepath": "demo.csv", "last_modified": datetime(2020, 6, 30, tzinfo=pytz.UTC)}],
            [
                {
                    "a": 1,
                    "b": "text",
                    "c": datetime(2021, 1, 1),
                    "_ab_file_last_modified": "2020-06-30T00:00:00+00:00",
                    "_ab_file_path": "demo.csv",
                },
                {
                    "a": 2,
                    "b": "text2",
                    "c": datetime(2021, 1, 2),
                    "_ab_file_last_modified": "2020-06-30T00:00:00+00:00",
                    "_ab_file_path": "demo.csv",
                },
            ],
        )
    ],
)
@patch("source_sftp.client.Client.read")
def test_read_stream_slice(mocked_read, records, stream_slice, expected, stream):
    mocked_read.return_value = records
    stream_records = list(stream.read_stream_slice(stream_slice))
    assert stream_records == expected


@pytest.mark.parametrize(
    "records, stream_slice, expected",
    [
        (
            [
                {"a": 1, "b": "text", "c": datetime(2021, 1, 1)},
                {"a": 2, "b": "text2", "c": datetime(2021, 1, 2)},
            ],
            [{"filepath": "demo.csv", "last_modified": datetime(2020, 6, 30, tzinfo=pytz.UTC)}],
            [
                {
                    "a": 1,
                    "b": "text",
                    "c": datetime(2021, 1, 1),
                    "_ab_file_last_modified": "2020-06-30T00:00:00+00:00",
                    "_ab_file_path": "demo.csv",
                },
                {
                    "a": 2,
                    "b": "text2",
                    "c": datetime(2021, 1, 2),
                    "_ab_file_last_modified": "2020-06-30T00:00:00+00:00",
                    "_ab_file_path": "demo.csv",
                },
            ],
        )
    ],
)
@patch("source_sftp.client.Client.read")
def test_read_records(mocked_read, records, stream_slice, expected, stream):
    mocked_read.return_value = records
    stream_records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
    assert stream_records == expected
