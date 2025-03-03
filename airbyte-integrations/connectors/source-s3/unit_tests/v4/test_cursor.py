#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone
from typing import Any, MutableMapping, Optional
from unittest.mock import Mock

import pytest
from source_s3.v4.cursor import Cursor

from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.cursor.default_file_based_cursor import DefaultFileBasedCursor


def _create_datetime(dt: str) -> datetime:
    return datetime.strptime(dt, DefaultFileBasedCursor.DATE_TIME_FORMAT)


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
                "v3_min_sync_date": "2023-07-31T23:00:00.000000Z",
            },
            id="single-date-single-file",
        ),
        pytest.param(
            {"history": {"2023-08-01": ["file1.txt"]}, "_ab_source_file_last_modified": "2023-08-01T02:03:04Z"},
            {
                "history": {
                    "file1.txt": "2023-08-01T02:03:04.000000Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T02:03:04.000000Z_file1.txt",
                "v3_min_sync_date": "2023-08-01T01:03:04.000000Z",
            },
            id="single-date-not-at-midnight-single-file",
        ),
        pytest.param(
            {"history": {"2023-08-01": ["file1.txt", "file2.txt"]}, "_ab_source_file_last_modified": "2023-08-01T00:00:00Z"},
            {
                "history": {
                    "file1.txt": "2023-08-01T00:00:00.000000Z",
                    "file2.txt": "2023-08-01T00:00:00.000000Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T00:00:00.000000Z_file2.txt",
                "v3_min_sync_date": "2023-07-31T23:00:00.000000Z",
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
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "v3_min_sync_date": "2023-07-31T23:00:00.000000Z",
                "_ab_source_file_last_modified": "2023-08-01T00:00:00.000000Z_file2.txt",
            },
            id="multiple-dates-multiple-files",
        ),
        pytest.param(
            {
                "history": {
                    "2023-08-01": ["file1.txt", "file2.txt"],
                    "2023-07-31": ["file1.txt", "file3.txt"],
                    "2023-07-30": ["file3.txt"],
                },
                "_ab_source_file_last_modified": "2023-08-01T10:11:12Z",
            },
            {
                "history": {
                    "file1.txt": "2023-08-01T10:11:12.000000Z",
                    "file2.txt": "2023-08-01T10:11:12.000000Z",
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T10:11:12.000000Z_file2.txt",
                "v3_min_sync_date": "2023-08-01T09:11:12.000000Z",
            },
            id="multiple-dates-multiple-files-not-at-midnight",
        ),
        pytest.param(
            {
                "history": {
                    "file1.txt": "2023-08-01T10:11:12.000000Z",
                    "file2.txt": "2023-08-01T10:11:12.000000Z",
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T10:11:12.000000Z_file2.txt",
            },
            {
                "history": {
                    "file1.txt": "2023-08-01T10:11:12.000000Z",
                    "file2.txt": "2023-08-01T10:11:12.000000Z",
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T10:11:12.000000Z_file2.txt",
            },
            id="v4-no-migration",
        ),
        pytest.param(
            {
                "history": {
                    "file1.txt": "2023-08-01T10:11:12.000000Z",
                    "file2.txt": "2023-08-01T10:11:12.000000Z",
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T10:11:12.000000Z_file2.txt",
                "v3_min_sync_date": "2023-07-31T23:00:00.000000Z",
            },
            {
                "history": {
                    "file1.txt": "2023-08-01T10:11:12.000000Z",
                    "file2.txt": "2023-08-01T10:11:12.000000Z",
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "v3_min_sync_date": "2023-07-31T23:00:00.000000Z",
                "_ab_source_file_last_modified": "2023-08-01T10:11:12.000000Z_file2.txt",
            },
            id="v4-migrated-from-v3",
        ),
        pytest.param(
            {"history": {}, "_ab_source_file_last_modified": "2023-08-01T00:00:00Z"},
            {
                "history": {},
                "_ab_source_file_last_modified": None,
                "v3_min_sync_date": "2023-07-31T23:00:00.000000Z",
            },
            id="empty-history-with-cursor",
        ),
    ],
)
def test_set_initial_state(input_state: MutableMapping[str, Any], expected_state: MutableMapping[str, Any]) -> None:
    cursor = _init_cursor_with_state(input_state)
    assert cursor.get_state() == expected_state


@pytest.mark.parametrize(
    "input_state, all_files, expected_files_to_sync, max_history_size",
    [
        pytest.param(
            {
                "history": {
                    "2023-08-01": ["file1.txt"],
                },
                "_ab_source_file_last_modified": "2023-08-01T00:00:00Z",
            },
            [RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T00:00:00.000000Z"))],
            [RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T00:00:00.000000Z"))],
            None,
            id="only_one_file_that_was_synced_exactly_at_midnight",
        ),
        pytest.param(
            {
                "history": {
                    "2023-08-01": ["file1.txt"],
                    "2023-08-02": ["file2.txt"],
                },
                "_ab_source_file_last_modified": "2023-08-02T00:06:00Z",
            },
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T00:00:00.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-02T06:00:00.000000Z")),
            ],
            [
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-02T06:00:00.000000Z")),
            ],
            None,
            id="do_not_sync_files_last_updated_on_a_previous_date",
        ),
        pytest.param(
            {
                "history": {
                    "2023-08-01": ["file1.txt"],
                    "2023-08-02": ["file2.txt"],
                },
                "_ab_source_file_last_modified": "2023-08-02T00:00:00Z",
            },
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T23:00:01.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-02T00:00:00.000000Z")),
            ],
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T23:00:01.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-02T00:00:00.000000Z")),
            ],
            None,
            id="sync_files_last_updated_within_one_hour_of_cursor",
        ),
        pytest.param(
            {
                "history": {
                    "2023-08-01": ["file1.txt", "file2.txt"],
                },
                "_ab_source_file_last_modified": "2023-08-01T02:00:00Z",
            },
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T01:30:00.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-01T02:00:00.000000Z")),
            ],
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T01:30:00.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-01T02:00:00.000000Z")),
            ],
            None,
            id="sync_files_last_updated_within_one_hour_of_cursor_on_same_day",
        ),
        pytest.param(
            {
                "history": {
                    "2023-08-01": ["file1.txt", "file2.txt"],
                },
                "_ab_source_file_last_modified": "2023-08-01T06:00:00Z",
            },
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T01:30:00.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-01T06:00:00.000000Z")),
            ],
            [
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-01T06:00:00.000000Z")),
            ],
            None,
            id="do_not_sync_files_last_modified_earlier_than_one_hour_before_cursor_on_same_day",
        ),
        pytest.param(
            {},
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T01:30:00.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-01T06:00:00.000000Z")),
            ],
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T01:30:00.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-01T06:00:00.000000Z")),
            ],
            None,
            id="no_state",
        ),
        pytest.param(
            {
                "history": {
                    "file1.txt": "2023-08-01T10:11:12.000000Z",
                    "file2.txt": "2023-08-01T10:11:12.000000Z",
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T10:11:12.000000Z_file2.txt",
            },
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file3.txt", last_modified=_create_datetime("2023-07-31T23:59:59.999999Z")),
            ],
            [],
            None,
            id="input_state_is_v4_no_new_files",
        ),
        pytest.param(
            {
                "history": {
                    "file1.txt": "2023-08-01T10:11:12.000000Z",
                    "file2.txt": "2023-08-01T10:11:12.000000Z",
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T10:11:12.000000Z_file2.txt",
            },
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file3.txt", last_modified=_create_datetime("2023-07-31T23:59:59.999999Z")),
                RemoteFile(uri="file4.txt", last_modified=_create_datetime("2023-08-02T00:00:00.000000Z")),
            ],
            [RemoteFile(uri="file4.txt", last_modified=_create_datetime("2023-08-02T00:00:00.000000Z"))],
            None,
            id="input_state_is_v4_with_new_file_later_than_cursor",
        ),
        pytest.param(
            {
                "history": {
                    "file1.txt": "2023-08-01T10:11:12.000000Z",
                    "file2.txt": "2023-08-01T10:11:12.000000Z",
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T10:11:12.000000Z_file2.txt",
            },
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file3.txt", last_modified=_create_datetime("2023-07-31T23:59:59.999999Z")),
                RemoteFile(uri="file4.txt", last_modified=_create_datetime("2023-08-01T00:00:00.000000Z")),
            ],
            [RemoteFile(uri="file4.txt", last_modified=_create_datetime("2023-08-01T00:00:00.000000Z"))],
            None,
            id="input_state_is_v4_with_new_file_earlier_than_cursor",
        ),
        pytest.param(
            {
                "history": {
                    "file1.txt": "2023-08-01T10:11:12.000000Z",
                    "file2.txt": "2023-08-01T10:11:12.000000Z",
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "v3_min_sync_date": "2023-07-16T00:00:00.000000Z",
                "_ab_source_file_last_modified": "2023-08-01T10:11:12.000000Z_file2.txt",
            },
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file3.txt", last_modified=_create_datetime("2023-07-31T23:59:59.999999Z")),
                RemoteFile(uri="file0.txt", last_modified=_create_datetime("2023-07-15T00:00:00.000000Z")),
            ],
            [],
            None,
            id="input_state_is_v4_with_a_new_file_earlier_than_migration_start_datetime",
        ),
        pytest.param(
            {
                "history": {
                    "file1.txt": "2023-08-01T10:11:12.000000Z",
                    "file2.txt": "2023-08-01T10:11:12.000000Z",
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "v3_min_sync_date": "2023-07-01T00:00:00.000000Z",
                "_ab_source_file_last_modified": "2023-08-01T10:11:12.000000Z_file2.txt",
            },
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file3.txt", last_modified=_create_datetime("2023-07-31T23:59:59.999999Z")),
                RemoteFile(uri="file0.txt", last_modified=_create_datetime("2023-07-15T00:00:00.000000Z")),
            ],
            [RemoteFile(uri="file0.txt", last_modified=_create_datetime("2023-07-15T00:00:00.000000Z"))],
            None,
            id="input_state_is_v4_with_a_new_file_later_than_migration_start_datetime",
        ),
        pytest.param(
            {
                "history": {
                    "file1.txt": "2023-08-01T10:11:12.000000Z",
                    "file2.txt": "2023-08-01T10:11:12.000000Z",
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "v3_min_sync_date": "2023-07-16T00:00:00.000000Z",
                "_ab_source_file_last_modified": "2023-08-01T10:11:12.000000Z_file2.txt",
            },
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file3.txt", last_modified=_create_datetime("2023-07-31T23:59:59.999999Z")),
                RemoteFile(uri="file0.txt", last_modified=_create_datetime("2023-07-15T00:00:00.000000Z")),
            ],
            [],
            3,
            id="input_state_is_v4_history_is_full_but_new_file_is_earlier_than_v3_min_sync_date",
        ),
        pytest.param(
            {
                "history": {
                    "file1.txt": "2023-08-01T10:11:12.000000Z",
                    "file2.txt": "2023-08-01T10:11:12.000000Z",
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "v3_min_sync_date": "2023-07-01T00:00:00.000000Z",
                "_ab_source_file_last_modified": "2023-08-01T10:11:12.000000Z_file2.txt",
            },
            [
                RemoteFile(uri="file1.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file2.txt", last_modified=_create_datetime("2023-08-01T10:11:12.000000Z")),
                RemoteFile(uri="file3.txt", last_modified=_create_datetime("2023-07-31T23:59:59.999999Z")),
                RemoteFile(uri="file0.txt", last_modified=_create_datetime("2023-07-15T00:00:00.000000Z")),
            ],
            [],  # file0.txt is not synced. It was presumably synced by v4 because its timestamp is later than v3_min_sync_date,
            # but it was kicked from the history because it was not in the top 3 most recently modified files.
            3,
            id="input_state_is_v4_history_is_full_and_new_file_is_later_than_v3_min_sync_date",
        ),
    ],
)
def test_list_files_v4_migration(input_state, all_files, expected_files_to_sync, max_history_size):
    cursor = _init_cursor_with_state(input_state, max_history_size)
    files_to_sync = list(cursor.get_files_to_sync(all_files, Mock()))
    assert files_to_sync == expected_files_to_sync


@pytest.mark.parametrize(
    "input_state, expected",
    [
        pytest.param({}, False, id="empty_state_is_not_legacy_state"),
        pytest.param(
            {"history": {"2023-08-01": ["file1.txt"]}, "_ab_source_file_last_modified": "2023-08-01T00:00:00Z"},
            True,
            id="legacy_state_with_history_and_last_modified_cursor_is_legacy_state",
        ),
        pytest.param(
            {"history": {"2023-08-01T00:00:00Z": ["file1.txt"]}, "_ab_source_file_last_modified": "2023-08-01T00:00:00Z"},
            False,
            id="legacy_state_with_invalid_history_date_format_is_not_legacy",
        ),
        pytest.param(
            {"history": {"2023-08-01": ["file1.txt"]}, "_ab_source_file_last_modified": "2023-08-01"},
            False,
            id="legacy_state_with_invalid_last_modified_datetime_format_is_not_legacy",
        ),
        pytest.param({"_ab_source_file_last_modified": "2023-08-01T00:00:00Z"}, True, id="legacy_state_without_history_is_legacy_state"),
        pytest.param({"history": {"2023-08-01": ["file1.txt"]}}, False, id="legacy_state_without_last_modified_cursor_is_not_legacy_state"),
        pytest.param(
            {
                "history": {
                    "file1.txt": "2023-08-01T10:11:12.000000Z",
                    "file2.txt": "2023-08-01T10:11:12.000000Z",
                    "file3.txt": "2023-07-31T23:59:59.999999Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T10:11:12.000000Z_file2.txt",
            },
            False,
            id="v4_state_format_is_not_legacy",
        ),
    ],
)
def test_is_legacy_state(input_state, expected):
    is_legacy_state = Cursor._is_legacy_state(input_state)
    assert is_legacy_state is expected


@pytest.mark.parametrize(
    "cursor_datetime, file_datetime, expected_adjusted_datetime",
    [
        pytest.param(
            datetime(2021, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc),
            datetime(2021, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc),
            datetime(2021, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc),
            id="cursor_datetime_equals_file_datetime_at_start_of_day",
        ),
        pytest.param(
            datetime(2021, 1, 1, 10, 11, 12, tzinfo=timezone.utc),
            datetime(2021, 1, 1, 10, 11, 12, tzinfo=timezone.utc),
            datetime(2021, 1, 1, 10, 11, 12, tzinfo=timezone.utc),
            id="cursor_datetime_equals_file_datetime_not_at_start_of_day",
        ),
        pytest.param(
            datetime(2021, 1, 1, 10, 11, 12, tzinfo=timezone.utc),
            datetime(2021, 1, 1, 0, 1, 2, tzinfo=timezone.utc),
            datetime(2021, 1, 1, 10, 11, 12, tzinfo=timezone.utc),
            id="cursor_datetime_same_day_but_later",
        ),
        pytest.param(
            datetime(2021, 1, 2, 0, 1, 2, tzinfo=timezone.utc),
            datetime(2021, 1, 1, 10, 11, 12, tzinfo=timezone.utc),
            datetime(2021, 1, 1, 23, 59, 59, 999999, tzinfo=timezone.utc),
            id="set_time_to_end_of_day_if_file_date_is_ealier_than_cursor_date",
        ),
        pytest.param(
            datetime(2021, 1, 1, 0, 1, 2, tzinfo=timezone.utc),
            datetime(2021, 1, 1, 10, 11, 12, tzinfo=timezone.utc),
            datetime(2021, 1, 1, 10, 11, 12, tzinfo=timezone.utc),
            id="file_datetime_is_unchanged_if_same_day_but_later_than_cursor_datetime",
        ),
        pytest.param(
            datetime(2021, 1, 1, 10, 11, 12, tzinfo=timezone.utc),
            datetime(2021, 1, 2, 0, 1, 2, tzinfo=timezone.utc),
            datetime(2021, 1, 2, 0, 1, 2, tzinfo=timezone.utc),
            id="file_datetime_is_unchanged_if_later_than_cursor_datetime",
        ),
    ],
)
def test_get_adjusted_date_timestamp(cursor_datetime, file_datetime, expected_adjusted_datetime):
    adjusted_datetime = Cursor._get_adjusted_date_timestamp(cursor_datetime, file_datetime)
    assert adjusted_datetime == expected_adjusted_datetime


def _init_cursor_with_state(input_state, max_history_size: Optional[int] = None) -> Cursor:
    cursor = Cursor(stream_config=FileBasedStreamConfig(name="test", validation_policy="Emit Record", format=CsvFormat()))
    cursor.set_initial_state(input_state)
    if max_history_size is not None:
        cursor.DEFAULT_MAX_HISTORY_SIZE = max_history_size
    return cursor
