# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from datetime import datetime

import pytest
from source_gcs import Cursor

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor


def test_add_file_successfully(cursor, remote_file, logger):
    cursor.add_file(remote_file)

    assert len(cursor._file_to_datetime_history) == 1


def test_add_file_successfully_with_full_history(cursor, remote_file, remote_file_b, logger):
    DefaultFileBasedCursor.DEFAULT_MAX_HISTORY_SIZE = 1

    cursor.add_file(remote_file)
    cursor.add_file(remote_file_b)

    assert len(cursor._file_to_datetime_history) == 1


def test_add_file_with_no_history(cursor, remote_file, remote_file_b, logger):
    DefaultFileBasedCursor.DEFAULT_MAX_HISTORY_SIZE = 0
    cursor.add_file(remote_file)
    cursor.add_file(remote_file_b)

    assert len(cursor._file_to_datetime_history) == 0


def test_get_files_to_sync_with_full_history(cursor, remote_file, remote_file_b, logger):
    DefaultFileBasedCursor.DEFAULT_MAX_HISTORY_SIZE = 1

    files_to_sync = list(cursor.get_files_to_sync([remote_file, remote_file_b], logger))

    assert len(files_to_sync) == 2


def test_get_files_to_sync_with_existing_file_in_history(cursor, remote_file, logger):
    cursor.add_file(remote_file)

    files_to_sync = list(cursor.get_files_to_sync([remote_file], logger))

    assert len(files_to_sync) == 0


def test_get_files_to_sync_with_existing_file_in_full_history(cursor, remote_file, remote_file_b, logger):
    DefaultFileBasedCursor.DEFAULT_MAX_HISTORY_SIZE = 1

    cursor.add_file(remote_file_b)

    files_to_sync = list(cursor.get_files_to_sync([remote_file], logger))

    assert len(files_to_sync) == 1


def test_get_files_to_sync_with_existing_newer_file(cursor, remote_file, remote_file_older, logger):
    cursor.add_file(remote_file)

    files_to_sync = list(cursor.get_files_to_sync([remote_file_older], logger))

    assert len(files_to_sync) == 0


def test_get_files_to_sync_with_existing_older_file(cursor, remote_file, remote_file_older, logger):
    DefaultFileBasedCursor.DEFAULT_MAX_HISTORY_SIZE = 1

    cursor.add_file(remote_file_older)
    cursor.add_file(remote_file)

    files_to_sync = list(cursor.get_files_to_sync([remote_file_older], logger))

    assert len(files_to_sync) == 0


def test_get_files_to_sync_with_existing_initial_state_and_newer_file(cursor, remote_file, remote_file_older, remote_file_b, logger):
    cursor.set_initial_state(
        {
            "history": {remote_file.uri: remote_file_older.last_modified.replace().strftime(cursor.DATE_TIME_FORMAT)},
            cursor.CURSOR_FIELD: cursor._get_cursor(),
        }
    )
    DefaultFileBasedCursor.DEFAULT_MAX_HISTORY_SIZE = 1

    files_to_sync = list(cursor.get_files_to_sync([remote_file], logger))

    assert len(files_to_sync) == 1


def test_get_files_to_sync_with_no_history(cursor, remote_file, logger):
    files_to_sync = list(cursor.get_files_to_sync([remote_file], logger))

    assert len(files_to_sync) == 1


def test_get_files_to_sync_with_same_time_as_initial_state(cursor, remote_file, logger):
    cursor.set_initial_state(
        {
            "history": {remote_file.uri: remote_file.last_modified.strftime(cursor.DATE_TIME_FORMAT)},
            cursor.CURSOR_FIELD: cursor._get_cursor(),
        }
    )

    files_to_sync = list(cursor.get_files_to_sync([remote_file], logger))

    assert len(files_to_sync) == 0


def test_get_files_to_sync_with_different_file_as_initial_state(cursor, remote_file, remote_file_older, logger):
    cursor.set_initial_state(
        {
            "history": {remote_file.uri: remote_file.last_modified.strftime(cursor.DATE_TIME_FORMAT)},
            cursor.CURSOR_FIELD: cursor._get_cursor(),
        }
    )
    DefaultFileBasedCursor.DEFAULT_MAX_HISTORY_SIZE = 1

    files_to_sync = list(cursor.get_files_to_sync([remote_file_older], logger))

    assert len(files_to_sync) == 1


def test_add_file_zip_files(mocked_reader, zip_file, logger):
    cursor = Cursor(stream_config=FileBasedStreamConfig(name="test", globs=["**/*.zip"], format={"filetype": "csv"}))
    cursor.add_file(zip_file)

    saved_history_cursor = datetime.strptime(cursor._file_to_datetime_history[zip_file.displayed_uri], cursor.DATE_TIME_FORMAT)

    assert saved_history_cursor == zip_file.last_modified


@pytest.mark.parametrize(
    "input_state,expected_history",
    [
        pytest.param(
            {
                "history": {
                    "https://storage.googleapis.com/my-bucket/path/to/file.csv": "2024-06-01T10:00:00.000000Z",
                    "https://storage.googleapis.com/my-bucket/other/data.jsonl": "2024-06-02T12:00:00.000000Z",
                },
                "_ab_source_file_last_modified": "2024-06-02T12:00:00.000000Z_https://storage.googleapis.com/my-bucket/other/data.jsonl",
            },
            {
                "gs://my-bucket/path/to/file.csv": "2024-06-01T10:00:00.000000Z",
                "gs://my-bucket/other/data.jsonl": "2024-06-02T12:00:00.000000Z",
            },
            id="migrates_signed_url_keys_to_gs_format",
        ),
        pytest.param(
            {
                "history": {
                    "gs://my-bucket/path/to/file.csv": "2024-06-01T10:00:00.000000Z",
                },
                "_ab_source_file_last_modified": "2024-06-01T10:00:00.000000Z_gs://my-bucket/path/to/file.csv",
            },
            {
                "gs://my-bucket/path/to/file.csv": "2024-06-01T10:00:00.000000Z",
            },
            id="already_gs_format_unchanged",
        ),
        pytest.param(
            {
                "history": {
                    "https://storage.googleapis.com/bucket/migrated.csv": "2024-06-01T10:00:00.000000Z",
                    "gs://bucket/already-clean.csv": "2024-06-02T12:00:00.000000Z",
                },
                "_ab_source_file_last_modified": "2024-06-02T12:00:00.000000Z_gs://bucket/already-clean.csv",
            },
            {
                "gs://bucket/migrated.csv": "2024-06-01T10:00:00.000000Z",
                "gs://bucket/already-clean.csv": "2024-06-02T12:00:00.000000Z",
            },
            id="mixed_old_and_new_format",
        ),
        pytest.param(
            {"history": {}},
            {},
            id="empty_history_unchanged",
        ),
        pytest.param(
            {},
            {},
            id="no_history_key_unchanged",
        ),
    ],
)
def test_state_migration_converts_signed_url_keys(stream_config, input_state, expected_history):
    """State migration must convert https://storage.googleapis.com/ keys to gs:// format."""
    cursor = Cursor(stream_config=stream_config)
    cursor.set_initial_state(input_state)

    assert dict(cursor._file_to_datetime_history) == expected_history
