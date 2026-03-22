import logging
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from source_s3.v4.cursor import Cursor


def _make_cursor(flatten_records_key="Records"):
    stream_config = MagicMock()
    stream_config.days_to_sync_if_history_is_full = 3
    # Set class-level attribute (mimics what SourceS3.streams() does)
    Cursor._flatten_records_key = flatten_records_key
    cursor = Cursor(stream_config)
    return cursor


def _make_file(uri: str, last_modified: datetime) -> RemoteFile:
    return RemoteFile(uri=uri, last_modified=last_modified)


class TestCloudTrailCursorMode:
    def test_cloudtrail_mode_enabled(self):
        cursor = _make_cursor(flatten_records_key="Records")
        assert cursor._cloudtrail_mode is True

    def test_cloudtrail_mode_disabled_when_no_key(self):
        cursor = _make_cursor(flatten_records_key=None)
        assert cursor._cloudtrail_mode is False

    def test_initial_state_no_cloudtrail_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"history": {"file.json": "2026-01-01T00:00:00.000000Z"}})
        assert cursor._cloudtrail_cursor_dt is None

    def test_initial_state_with_cloudtrail_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({
            "history": {},
            "cloudtrail_cursor": "2026-03-20T10:00:00.000000Z",
        })
        assert cursor._cloudtrail_cursor_dt == datetime(2026, 3, 20, 10, 0, 0)

    def test_should_sync_file_newer_than_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        file = _make_file("new.json", datetime(2026, 3, 21, 5, 0, 0))
        assert cursor._should_sync_file(file, logging.getLogger()) is True

    def test_should_not_sync_file_older_than_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        file = _make_file("old.json", datetime(2026, 3, 19, 5, 0, 0))
        assert cursor._should_sync_file(file, logging.getLogger()) is False

    def test_should_not_sync_file_equal_to_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        file = _make_file("same.json", datetime(2026, 3, 20, 10, 0, 0))
        assert cursor._should_sync_file(file, logging.getLogger()) is False

    def test_add_file_advances_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        cursor.add_file(_make_file("new.json", datetime(2026, 3, 21, 5, 0, 0)))
        assert cursor._cloudtrail_cursor_dt == datetime(2026, 3, 21, 5, 0, 0)

    def test_add_file_does_not_regress_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-21T10:00:00.000000Z"})
        cursor.add_file(_make_file("old.json", datetime(2026, 3, 20, 5, 0, 0)))
        assert cursor._cloudtrail_cursor_dt == datetime(2026, 3, 21, 10, 0, 0)

    def test_add_file_does_not_populate_history(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        cursor.add_file(_make_file("new.json", datetime(2026, 3, 21, 5, 0, 0)))
        assert cursor._file_to_datetime_history == {}

    def test_get_state_includes_cloudtrail_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        cursor.add_file(_make_file("new.json", datetime(2026, 3, 21, 5, 0, 0)))
        state = cursor.get_state()
        assert state["cloudtrail_cursor"] == "2026-03-21T05:00:00.000000Z"
        assert state["history"] == {}

    def test_get_cursor_returns_cloudtrail_cursor_for_ui(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        state = cursor.get_state()
        assert state[DefaultFileBasedCursor.CURSOR_FIELD] is not None

    def test_non_cloudtrail_mode_delegates_to_super(self):
        cursor = _make_cursor(flatten_records_key=None)
        cursor.set_initial_state({})
        file = _make_file("any.json", datetime(2026, 3, 21, 5, 0, 0))
        assert cursor._should_sync_file(file, logging.getLogger()) is True


class TestCloudTrailFirstSyncWithStartDate:
    """First sync: no cloudtrail_cursor in state, uses start_date to filter."""

    def test_syncs_file_newer_than_start_date(self):
        Cursor._start_date = "2026-03-20T10:00:00.000000Z"
        cursor = _make_cursor()
        cursor.set_initial_state({})  # No cloudtrail_cursor
        file = _make_file("new.json", datetime(2026, 3, 21, 5, 0, 0))
        assert cursor._should_sync_file(file, logging.getLogger()) is True

    def test_skips_file_older_than_start_date(self):
        Cursor._start_date = "2026-03-20T10:00:00.000000Z"
        cursor = _make_cursor()
        cursor.set_initial_state({})  # No cloudtrail_cursor
        file = _make_file("old.json", datetime(2026, 3, 19, 5, 0, 0))
        assert cursor._should_sync_file(file, logging.getLogger()) is False

    def test_skips_file_equal_to_start_date(self):
        Cursor._start_date = "2026-03-20T10:00:00.000000Z"
        cursor = _make_cursor()
        cursor.set_initial_state({})
        file = _make_file("same.json", datetime(2026, 3, 20, 10, 0, 0))
        assert cursor._should_sync_file(file, logging.getLogger()) is False

    def test_no_start_date_syncs_everything(self):
        Cursor._start_date = None
        cursor = _make_cursor()
        cursor.set_initial_state({})
        file = _make_file("any.json", datetime(2020, 1, 1, 0, 0, 0))
        assert cursor._should_sync_file(file, logging.getLogger()) is True
