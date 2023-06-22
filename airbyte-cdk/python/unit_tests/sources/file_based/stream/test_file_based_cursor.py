#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.file_based_cursor import DATE_TIME_FORMAT, FileBasedCursor
from freezegun import freeze_time


@pytest.mark.parametrize(
    "files_to_add, expected_start_time, expected_state_dict",
    [
        pytest.param([
            RemoteFile(uri="a.csv",
                       last_modified=datetime.strptime("2021-01-01T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv"),
            RemoteFile(uri="b.csv",
                       last_modified=datetime.strptime("2021-01-02T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv"),
            RemoteFile(uri="c.csv",
                       last_modified=datetime.strptime("2020-12-31T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv")

        ],
            [datetime(2021, 1, 1),
             datetime(2021, 1, 1),
             datetime(2020, 12, 31)],
            {"history": {
                "a.csv": "2021-01-01T00:00:00.000000Z",
                "b.csv": "2021-01-02T00:00:00.000000Z",
                "c.csv": "2020-12-31T00:00:00.000000Z",
            }, "history_is_partial": False},
            id="test_file_start_time_is_earliest_time_in_history"),
        pytest.param([
            RemoteFile(uri="a.csv",
                       last_modified=datetime.strptime("2021-01-01T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv"),
            RemoteFile(uri="b.csv",
                       last_modified=datetime.strptime("2021-01-02T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv"),
            RemoteFile(uri="c.csv",
                       last_modified=datetime.strptime("2021-01-03T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv"),
            RemoteFile(uri="d.csv",
                       last_modified=datetime.strptime("2021-01-04T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv"),

        ],
            [datetime(2021, 1, 1),
             datetime(2021, 1, 1),
             datetime(2021, 1, 1),
             datetime(2021, 1, 2)],
            {"history": {
                "b.csv": "2021-01-02T00:00:00.000000Z",
                "c.csv": "2021-01-03T00:00:00.000000Z",
                "d.csv": "2021-01-04T00:00:00.000000Z",
            }, "history_is_partial": False},
            id="test_earliest_file_is_removed_from_history_if_history_is_full"),
        pytest.param([
            RemoteFile(uri="a.csv",
                       last_modified=datetime.strptime("2021-01-01T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv"),
            RemoteFile(uri="file_with_same_timestamp_as_b.csv",
                       last_modified=datetime.strptime("2021-01-02T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv"),
            RemoteFile(uri="b.csv",
                       last_modified=datetime.strptime("2021-01-02T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv"),
            RemoteFile(uri="c.csv",
                       last_modified=datetime.strptime("2021-01-03T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv"),
            RemoteFile(uri="d.csv",
                       last_modified=datetime.strptime("2021-01-04T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv"),

        ],
            [datetime(2021, 1, 1),
             datetime(2021, 1, 1),
             datetime(2021, 1, 1),
             datetime(2021, 1, 2),
             datetime(2021, 1, 2),
             ],
            {"history": {
                "file_with_same_timestamp_as_b.csv": "2021-01-02T00:00:00.000000Z",
                "c.csv": "2021-01-03T00:00:00.000000Z",
                "d.csv": "2021-01-04T00:00:00.000000Z",
            }, "history_is_partial": False},
            id="test_files_are_sorted_by_timestamp_and_by_name"),
    ],
)
def test_add_file(files_to_add, expected_start_time, expected_state_dict):
    logger = MagicMock()
    cursor = FileBasedCursor(3, timedelta(days=3), logger)
    assert cursor._compute_start_time() == datetime.min

    for index, f in enumerate(files_to_add):
        cursor.add_file(f)
        assert expected_start_time[index] == cursor._compute_start_time()
    assert expected_state_dict == cursor.get_state()


@pytest.mark.parametrize("files, expected_files_to_sync, max_history_size, history_is_partial", [
    pytest.param([
        RemoteFile(uri="a.csv",
                   last_modified=datetime.strptime("2021-01-01T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                   file_type="csv"),
        RemoteFile(uri="b.csv",
                   last_modified=datetime.strptime("2021-01-02T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                   file_type="csv"),
        RemoteFile(uri="c.csv",
                   last_modified=datetime.strptime("2020-12-31T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                   file_type="csv")
    ],
        [
            RemoteFile(uri="a.csv",
                       last_modified=datetime.strptime("2021-01-01T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv"),
            RemoteFile(uri="b.csv",
                       last_modified=datetime.strptime("2021-01-02T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv"),
            RemoteFile(uri="c.csv",
                       last_modified=datetime.strptime("2020-12-31T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                       file_type="csv")
        ], 3, False, id="test_all_files_should_be_synced"),
    pytest.param([
        RemoteFile(uri="a.csv",
                   last_modified=datetime.strptime("2021-01-01T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                   file_type="csv"),
        RemoteFile(uri="b.csv",
                   last_modified=datetime.strptime("2021-01-02T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                   file_type="csv"),
        RemoteFile(uri="c.csv",
                   last_modified=datetime.strptime("2020-12-31T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                   file_type="csv")
    ], [
        RemoteFile(uri="a.csv",
                   last_modified=datetime.strptime("2021-01-01T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                   file_type="csv"),
        RemoteFile(uri="b.csv",
                   last_modified=datetime.strptime("2021-01-02T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                   file_type="csv"),
        RemoteFile(uri="c.csv",
                   last_modified=datetime.strptime("2020-12-31T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                   file_type="csv")

    ], 2, True, id="test_sync_more_files_than_history_size")
])
def test_get_files_to_sync(files, expected_files_to_sync, max_history_size, history_is_partial):
    logger = MagicMock()
    cursor = FileBasedCursor(max_history_size, timedelta(days=3), logger)

    files_to_sync = cursor.get_files_to_sync(files)

    assert files_to_sync == expected_files_to_sync
    assert cursor.is_history_partial() == history_is_partial
    if history_is_partial:
        logger.warning.assert_called_once()
    else:
        logger.warning.assert_not_called()


@pytest.mark.parametrize("history_is_partial", [
    pytest.param(True, id="test_history_is_partial"),
    pytest.param(False, id="test_history_is_not_partial"),
])
def test_files_are_not_synced_if_they_are_in_history(history_is_partial):
    logger = MagicMock()
    cursor = FileBasedCursor(2, timedelta(days=3), logger)

    files = [
        RemoteFile(uri="a.csv", last_modified=datetime(2021, 1, 1), file_type="csv"),
        RemoteFile(uri="b.csv", last_modified=datetime(2021, 1, 2), file_type="csv"),
    ]

    cursor._file_to_datetime_history = {
        f.uri: f.last_modified for f in files
    }
    cursor._history_is_partial = history_is_partial

    files_to_sync = cursor.get_files_to_sync(files)

    assert len(files_to_sync) == 0


@freeze_time("2023-06-16T00:00:00Z")
def test_only_recent_files_are_synced_if_history_is_full():
    logger = MagicMock()
    cursor = FileBasedCursor(2, timedelta(days=3), logger)
    cursor._history_is_partial = True

    files_in_history = [
        RemoteFile(uri="b1.csv", last_modified=datetime(2021, 1, 2), file_type="csv"),
        RemoteFile(uri="b2.csv", last_modified=datetime(2021, 1, 3), file_type="csv"),
    ]

    state = {
        "history": {
            f.uri: f.last_modified.strftime(DATE_TIME_FORMAT) for f in files_in_history
        },
        "history_is_partial": True
    }
    cursor.set_initial_state(state)

    files = [
        RemoteFile(uri="a.csv", last_modified=datetime(2021, 1, 1), file_type="csv"),
        RemoteFile(uri="c.csv", last_modified=datetime(2021, 1, 2), file_type="csv"),
        RemoteFile(uri="d.csv", last_modified=datetime(2021, 1, 4), file_type="csv"),
    ]

    expected_files_to_sync = [
        RemoteFile(uri="c.csv", last_modified=datetime(2021, 1, 2), file_type="csv"),
        RemoteFile(uri="d.csv", last_modified=datetime(2021, 1, 4), file_type="csv"),
    ]

    files_to_sync = cursor.get_files_to_sync(files)
    assert files_to_sync == expected_files_to_sync


@pytest.mark.parametrize("earliest_file_in_history, expected_start_time", [
    pytest.param(RemoteFile(uri="a.csv", last_modified=datetime(2023, 6, 15), file_type="csv"),
                 datetime(2023, 6, 13), id="test_start_time_is_time_window_if_file_is_recent"),
    pytest.param(RemoteFile(uri="a.csv", last_modified=datetime(2023, 6, 10), file_type="csv"),
                 datetime(2023, 6, 10), id="test_start_time_is_time_of_last_file_if_it_is_older_than_time_window"),
])
@freeze_time("2023-06-16T00:00:00Z")
def test_compute_if_history_is_partial(earliest_file_in_history, expected_start_time):
    logger = MagicMock()
    cursor = FileBasedCursor(3, timedelta(days=3), logger)
    cursor.add_file(earliest_file_in_history)
    cursor._history_is_partial = True
    assert cursor._compute_start_time() == expected_start_time
