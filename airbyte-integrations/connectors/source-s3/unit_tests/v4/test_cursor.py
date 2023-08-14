#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, MutableMapping
from unittest.mock import Mock

import pytest
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
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
            {"history": {"2023-08-01": ["file1.txt"]}, "_ab_source_file_last_modified": "2023-08-01T02:03:04Z"},
            {
                "history": {
                    "file1.txt": "2023-08-01T02:03:04.000000Z",
                },
                "_ab_source_file_last_modified": "2023-08-01T02:03:04.000000Z_file1.txt",
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
            },
            id="multiple-dates-multiple-files-not-at-midnight",
        ),
    ],
)
def test_set_initial_state_with_v3_state(input_state: MutableMapping[str, Any], expected_state: MutableMapping[str, Any]) -> None:
    cursor = Cursor(stream_config=FileBasedStreamConfig(file_type="csv", name="test", validation_policy="Emit Record"))
    cursor.set_initial_state(input_state)
    assert cursor.get_state() == expected_state


def test_v4_migration_only_one_file_that_was_synced_exactly_at_midnight():
    legacy_state = {
        "history": {
            "2023-08-01": ["file1.txt"],
        },
        "_ab_source_file_last_modified": "2023-08-01T00:00:00Z",
    }
    cursor = Cursor(stream_config=FileBasedStreamConfig(file_type="csv", name="test", validation_policy="Emit Record"))
    cursor.set_initial_state(legacy_state)

    all_files = [RemoteFile(uri="file1.txt", last_modified="2023-08-01T00:00:00.000000Z")]
    logger = Mock()

    files_to_sync = list(cursor.get_files_to_sync(all_files, logger))

    expected_files_to_sync = [
        RemoteFile(uri="file1.txt", last_modified="2023-08-01T00:00:00.000000Z"),
    ]

    assert files_to_sync == expected_files_to_sync


def test_v4_migration_do_not_sync_files_last_updated_on_a_previous_date():
    legacy_state = {
        "history": {
            "2023-08-01": ["file1.txt"],
            "2023-08-02": ["file2.txt"],
        },
        "_ab_source_file_last_modified": "2023-08-02T00:06:00Z",
    }
    cursor = Cursor(stream_config=FileBasedStreamConfig(file_type="csv", name="test", validation_policy="Emit Record"))
    cursor.set_initial_state(legacy_state)

    all_files = [
        RemoteFile(uri="file1.txt", last_modified="2023-08-01T00:00:00.000000Z"),
        RemoteFile(uri="file2.txt", last_modified="2023-08-02T06:00:00.000000Z"),
    ]
    logger = Mock()

    files_to_sync = list(cursor.get_files_to_sync(all_files, logger))

    expected_files_to_sync = [
        RemoteFile(uri="file2.txt", last_modified="2023-08-02T06:00:00.000000Z"),
    ]

    assert files_to_sync == expected_files_to_sync


def test_v4_migration_sync_files_last_updated_within_one_hour_of_cursor_even_if_on_different_day():
    legacy_state = {
        "history": {
            "2023-08-01": ["file1.txt"],
            "2023-08-02": ["file2.txt"],
        },
        "_ab_source_file_last_modified": "2023-08-02T00:00:00Z",
    }
    cursor = Cursor(stream_config=FileBasedStreamConfig(file_type="csv", name="test", validation_policy="Emit Record"))
    cursor.set_initial_state(legacy_state)

    all_files = [
        RemoteFile(uri="file1.txt", last_modified="2023-08-01T23:00:01.000000Z"),
        RemoteFile(uri="file2.txt", last_modified="2023-08-02T00:00:00.000000Z"),
    ]
    logger = Mock()

    files_to_sync = list(cursor.get_files_to_sync(all_files, logger))

    expected_files_to_sync = [
        RemoteFile(uri="file1.txt", last_modified="2023-08-01T23:00:01.000000Z"),
        RemoteFile(uri="file2.txt", last_modified="2023-08-02T00:00:00.000000Z"),
    ]

    assert files_to_sync == expected_files_to_sync


def test_v4_migration_sync_files_last_updated_within_one_hour_of_cursor_on_same_day():
    legacy_state = {
        "history": {
            "2023-08-01": ["file1.txt", "file2.txt"],
        },
        "_ab_source_file_last_modified": "2023-08-01T02:00:00Z",
    }
    cursor = Cursor(stream_config=FileBasedStreamConfig(file_type="csv", name="test", validation_policy="Emit Record"))
    cursor.set_initial_state(legacy_state)

    all_files = [
        RemoteFile(uri="file1.txt", last_modified="2023-08-01T01:30:00.000000Z"),
        RemoteFile(uri="file2.txt", last_modified="2023-08-01T02:00:00.000000Z"),
    ]
    logger = Mock()

    files_to_sync = list(cursor.get_files_to_sync(all_files, logger))

    expected_files_to_sync = [
        RemoteFile(uri="file1.txt", last_modified="2023-08-01T01:30:00.000000Z"),
        RemoteFile(uri="file2.txt", last_modified="2023-08-01T02:00:00.000000Z"),
    ]

    assert files_to_sync == expected_files_to_sync


def test_v4_migration_do_not_sync_files_last_earlier_than_one_hour_of_cursor_on_same_day():
    legacy_state = {
        "history": {
            "2023-08-01": ["file1.txt", "file2.txt"],
        },
        "_ab_source_file_last_modified": "2023-08-01T06:00:00Z",
    }
    cursor = Cursor(stream_config=FileBasedStreamConfig(file_type="csv", name="test", validation_policy="Emit Record"))
    cursor.set_initial_state(legacy_state)

    all_files = [
        RemoteFile(uri="file1.txt", last_modified="2023-08-01T01:30:00.000000Z"),
        RemoteFile(uri="file2.txt", last_modified="2023-08-01T06:00:00.000000Z"),
    ]
    logger = Mock()

    files_to_sync = list(cursor.get_files_to_sync(all_files, logger))

    expected_files_to_sync = [
        RemoteFile(uri="file2.txt", last_modified="2023-08-01T06:00:00.000000Z"),
    ]

    assert files_to_sync == expected_files_to_sync
