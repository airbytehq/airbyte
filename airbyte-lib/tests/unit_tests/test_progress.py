# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import datetime
from textwrap import dedent
import time
import pytest
from freezegun import freeze_time
from airbyte_lib.progress import ReadProgress, _get_elapsed_time_str, _to_time_str
from dateutil.tz import tzlocal

# Calculate the offset from UTC in hours
tz_offset_hrs = int(datetime.datetime.now(tzlocal()).utcoffset().total_seconds() / 3600)


@freeze_time("2022-01-01")
def test_read_progress_initialization():
    progress = ReadProgress()
    assert progress.num_streams_expected == 0
    assert progress.read_start_time == 1640995200.0  # Unix timestamp for 2022-01-01
    assert progress.total_records_read == 0
    assert progress.total_records_written == 0
    assert progress.total_batches_written == 0
    assert progress.written_stream_names == set()
    assert progress.finalize_start_time is None
    assert progress.finalize_end_time is None
    assert progress.total_records_finalized == 0
    assert progress.total_batches_finalized == 0
    assert progress.finalized_stream_names == set()
    assert progress.last_update_time is None


@freeze_time("2022-01-01")
def test_read_progress_reset():
    progress = ReadProgress()
    progress.reset(5)
    assert progress.num_streams_expected == 5
    assert progress.read_start_time == 1640995200.0
    assert progress.total_records_read == 0
    assert progress.total_records_written == 0
    assert progress.total_batches_written == 0
    assert progress.written_stream_names == set()
    assert progress.finalize_start_time is None
    assert progress.finalize_end_time is None
    assert progress.total_records_finalized == 0
    assert progress.total_batches_finalized == 0
    assert progress.finalized_stream_names == set()

@freeze_time("2022-01-01")
def test_read_progress_log_records_read():
    progress = ReadProgress()
    progress.log_records_read(100)
    assert progress.total_records_read == 100

@freeze_time("2022-01-01")
def test_read_progress_log_batch_written():
    progress = ReadProgress()
    progress.log_batch_written("stream1", 50)
    assert progress.total_records_written == 50
    assert progress.total_batches_written == 1
    assert progress.written_stream_names == {"stream1"}

@freeze_time("2022-01-01")
def test_read_progress_log_batches_finalizing():
    progress = ReadProgress()
    progress.log_batches_finalizing("stream1", 1)
    assert progress.finalize_start_time == 1640995200.0

@freeze_time("2022-01-01")
def test_read_progress_log_batches_finalized():
    progress = ReadProgress()
    progress.log_batches_finalized("stream1", 1)
    assert progress.total_batches_finalized == 1

@freeze_time("2022-01-01")
def test_read_progress_log_stream_finalized():
    progress = ReadProgress()
    progress.log_stream_finalized("stream1")
    assert progress.finalized_stream_names == {"stream1"}


def test_get_elapsed_time_str():
    assert _get_elapsed_time_str(30) == "30 seconds"
    assert _get_elapsed_time_str(90) == "1min 30s"
    assert _get_elapsed_time_str(600) == "10min"
    assert _get_elapsed_time_str(3600) == "1hr 0min"


@freeze_time("2022-01-01 0:00:00")
def test_get_time_str():
    assert _to_time_str(time.time()) == "00:00:00"


def _assert_lines(expected_lines, actual_lines: list[str] | str):
    if isinstance(actual_lines, list):
        actual_lines = "\n".join(actual_lines)
    for line in expected_lines:
        assert line in actual_lines, f"Missing line: {line}"

def test_get_status_message_after_finalizing_records():

    # Test that we can render the initial status message before starting to read
    with freeze_time("2022-01-01 00:00:00"):
        progress = ReadProgress()
        expected_lines = [
            "Started reading at 00:00:00.",
            "Read **0** records over **0 seconds** (0.0 records / second).",
        ]
        _assert_lines(expected_lines, progress._get_status_message())

    # Test after reading some records
    with freeze_time("2022-01-01 00:01:00"):
        progress.log_records_read(100)
        expected_lines = [
            "Started reading at 00:00:00.",
            "Read **100** records over **60 seconds** (1.7 records / second).",
        ]
        _assert_lines(expected_lines, progress._get_status_message())

    # Advance the day and reset the progress
    with freeze_time("2022-01-02 00:00:00"):
        progress = ReadProgress()
        progress.reset(1)
        expected_lines = [
            "Started reading at 00:00:00.",
            "Read **0** records over **0 seconds** (0.0 records / second).",
        ]
        _assert_lines(expected_lines, progress._get_status_message())

    # Test after writing some records and starting to finalize
    with freeze_time("2022-01-02 00:01:00"):
        progress.log_records_read(100)
        progress.log_batch_written("stream1", 50)
        progress.log_batches_finalizing("stream1", 1)
        expected_lines = [
            "## Read Progress",
            "Started reading at 00:00:00.",
            "Read **100** records over **60 seconds** (1.7 records / second).",
            "Wrote **50** records over 1 batches.",
            "Finished reading at 00:01:00.",
            "Started finalizing streams at 00:01:00.",
        ]
        _assert_lines(expected_lines, progress._get_status_message())

    # Test after finalizing some records
    with freeze_time("2022-01-02 00:02:00"):
        progress.log_batches_finalized("stream1", 1)
        expected_lines = [
            "## Read Progress",
            "Started reading at 00:00:00.",
            "Read **100** records over **60 seconds** (1.7 records / second).",
            "Wrote **50** records over 1 batches.",
            "Finished reading at 00:01:00.",
            "Started finalizing streams at 00:01:00.",
            "Finalized **1** batches over 60 seconds.",
        ]
        _assert_lines(expected_lines, progress._get_status_message())

    # Test after finalizing all records
    with freeze_time("2022-01-02 00:02:00"):
        progress.log_stream_finalized("stream1")
        message = progress._get_status_message()
        expected_lines = [
            "## Read Progress",
            "Started reading at 00:00:00.",
            "Read **100** records over **60 seconds** (1.7 records / second).",
            "Wrote **50** records over 1 batches.",
            "Finished reading at 00:01:00.",
            "Started finalizing streams at 00:01:00.",
            "Finalized **1** batches over 60 seconds.",
            "Completed 1 out of 1 streams:",
            "- stream1",
            "Total time elapsed: 2min 0s",
        ]
        _assert_lines(expected_lines, message)
