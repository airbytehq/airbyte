from textwrap import dedent
import pytest
from freezegun import freeze_time
from airbyte_lib.progress import ReadProgress, get_elapsed_time_str

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
def test_read_progress_log_batch_finalizing():
    progress = ReadProgress()
    progress.log_batch_finalizing("stream1")
    assert progress.finalize_start_time == 1640995200.0

@freeze_time("2022-01-01")
def test_read_progress_log_batch_finalized():
    progress = ReadProgress()
    progress.log_batch_finalized("stream1")
    assert progress.total_batches_finalized == 1

@freeze_time("2022-01-01")
def test_read_progress_log_stream_finalized():
    progress = ReadProgress()
    progress.log_stream_finalized("stream1")
    assert progress.finalized_stream_names == {"stream1"}


def test_get_elapsed_time_str():
    assert get_elapsed_time_str(30) == "30 seconds"
    assert get_elapsed_time_str(90) == "1min 30s"
    assert get_elapsed_time_str(600) == "10min"
    assert get_elapsed_time_str(3600) == "1hr 0min"


@freeze_time("2022-01-01 0:00:00")
def test_status_initial_state():
    progress = ReadProgress()

    message = progress._get_status_message()
    assert message.splitlines() == dedent(
        """
        ## Read Progress

        Started reading at 00:00:00.

        Read **0** records over **0 seconds** (0.0 records / second).


        ------------------------------------------------
        """
    ).lstrip().splitlines()


@freeze_time("2022-01-01 0:00:00")
def test_status_10s_elapsed():
    progress = ReadProgress()

    # Freeze time ten seconds later.
    with freeze_time("2022-01-01 0:00:10"):
        message = progress._get_status_message()

    assert message.splitlines() == dedent(
        """
        ## Read Progress

        Started reading at 00:00:00.

        Read **0** records over **10 seconds** (0.0 records / second).


        ------------------------------------------------
        """
    ).lstrip().splitlines()


def test_get_status_message_after_reading_records():
    with freeze_time("2022-01-01 00:00:00"):
        progress = ReadProgress()

    with freeze_time("2022-01-01 00:01:00"):
        progress.log_records_read(100)
        message = progress._get_status_message()

    assert message.splitlines() == dedent(
        """
        ## Read Progress

        Started reading at 00:00:00.

        Read **100** records over **60 seconds** (1.7 records / second).


        ------------------------------------------------
        """
    ).lstrip().splitlines()


@freeze_time("2022-01-01 00:01:00")
def test_get_status_message_after_writing_records():
    with freeze_time("2022-01-01 00:00:00"):
        progress = ReadProgress()

    with freeze_time("2022-01-01 00:01:00"):
        progress.log_records_read(100)
        progress.log_batch_written("stream1", 50)
        message = progress._get_status_message()

    assert message.splitlines() == dedent(
        """
        ## Read Progress

        Started reading at 00:00:00.

        Read **100** records over **60 seconds** (1.7 records / second).

        Wrote **50** records over 1 batches.


        ------------------------------------------------
        """
    ).lstrip().splitlines()


def test_get_status_message_after_finalizing_records():
    with freeze_time("2022-01-01 00:00:00"):
        progress = ReadProgress()

    with freeze_time("2022-01-01 00:01:00"):
        progress.log_records_read(100)
        progress.log_batch_written("stream1", 50)
        progress.log_batch_finalizing("stream1")

    with freeze_time("2022-01-01 00:02:00"):
        progress.log_batch_finalized("stream1")
        message = progress._get_status_message()

    assert message.splitlines() == dedent(
        """
        ## Read Progress

        Started reading at 00:00:00.

        Read **100** records over **60 seconds** (1.7 records / second).

        Wrote **50** records over 1 batches.

        Finished reading at 00:01:00.

        Started finalizing streams at 00:01:00.

        Finalized **1** batches over 60 seconds.

        ------------------------------------------------
        """
    ).lstrip().splitlines()
