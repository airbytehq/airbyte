# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from datetime import datetime
from typing import Any, Dict, List, MutableMapping, Optional, Tuple
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.concurrent.adapters import FileBasedStreamPartition
from airbyte_cdk.sources.file_based.stream.concurrent.cursor import FileBasedConcurrentCursor
from airbyte_cdk.sources.streams.concurrent.cursor import CursorField
from freezegun import freeze_time

DATE_TIME_FORMAT = FileBasedConcurrentCursor.DATE_TIME_FORMAT
MOCK_DAYS_TO_SYNC_IF_HISTORY_IS_FULL = 3


def _make_cursor(input_state: Optional[MutableMapping[str, Any]]) -> FileBasedConcurrentCursor:
    stream = MagicMock()
    stream.name = "test"
    stream.namespace = None
    stream_config = MagicMock()
    stream_config.days_to_sync_if_history_is_full = MOCK_DAYS_TO_SYNC_IF_HISTORY_IS_FULL
    cursor = FileBasedConcurrentCursor(
        stream_config,
        stream.name,
        None,
        input_state,
        MagicMock(),
        ConnectorStateManager(
            stream_instance_map={stream.name: stream},
            state=[AirbyteStateMessage.parse_obj(input_state)] if input_state is not None else None,
        ),
        CursorField(FileBasedConcurrentCursor.CURSOR_FIELD),
    )
    return cursor


@pytest.mark.parametrize(
    "input_state, expected_cursor_value",
    [
        pytest.param({}, (datetime.min, ""), id="no-state-gives-min-cursor"),
        pytest.param({"history": {}}, (datetime.min, ""), id="missing-cursor-field-gives-min-cursor"),
        pytest.param(
            {"history": {"a.csv": "2021-01-01T00:00:00.000000Z"}, "_ab_source_file_last_modified": "2021-01-01T00:00:00.000000Z_a.csv"},
            (datetime.strptime("2021-01-01T00:00:00.000000Z", DATE_TIME_FORMAT), "a.csv"),
            id="cursor-value-matches-earliest-file",
        ),
        pytest.param(
            {"history": {"a.csv": "2021-01-01T00:00:00.000000Z"}, "_ab_source_file_last_modified": "2020-01-01T00:00:00.000000Z_a.csv"},
            (datetime.strptime("2020-01-01T00:00:00.000000Z", DATE_TIME_FORMAT), "a.csv"),
            id="cursor-value-is-earlier",
        ),
        pytest.param(
            {"history": {"a.csv": "2022-01-01T00:00:00.000000Z"}, "_ab_source_file_last_modified": "2021-01-01T00:00:00.000000Z_a.csv"},
            (datetime.strptime("2021-01-01T00:00:00.000000Z", DATE_TIME_FORMAT), "a.csv"),
            id="cursor-value-is-later",
        ),
        pytest.param(
            {
                "history": {
                    "a.csv": "2021-01-01T00:00:00.000000Z",
                    "b.csv": "2021-01-02T00:00:00.000000Z",
                    "c.csv": "2021-01-03T00:00:00.000000Z",
                },
                "_ab_source_file_last_modified": "2021-01-04T00:00:00.000000Z_d.csv",
            },
            (datetime.strptime("2021-01-01T00:00:00.000000Z", DATE_TIME_FORMAT), "a.csv"),
            id="cursor-not-earliest",
        ),
        pytest.param(
            {"history": {"b.csv": "2020-12-31T00:00:00.000000Z"}, "_ab_source_file_last_modified": "2021-01-01T00:00:00.000000Z_a.csv"},
            (datetime.strptime("2020-12-31T00:00:00.000000Z", DATE_TIME_FORMAT), "b.csv"),
            id="state-with-cursor-and-earlier-history",
        ),
        pytest.param(
            {"history": {"b.csv": "2021-01-02T00:00:00.000000Z"}, "_ab_source_file_last_modified": "2021-01-01T00:00:00.000000Z_a.csv"},
            (datetime.strptime("2021-01-01T00:00:00.000000Z", DATE_TIME_FORMAT), "a.csv"),
            id="state-with-cursor-and-later-history",
        ),
    ],
)
def test_compute_prev_sync_cursor(input_state: MutableMapping[str, Any], expected_cursor_value: Tuple[datetime, str]):
    cursor = _make_cursor(input_state)
    assert cursor._compute_prev_sync_cursor(input_state) == expected_cursor_value


@pytest.mark.parametrize(
    "initial_state, pending_files, file_to_add, expected_history, expected_pending_files, expected_cursor_value",
    [
        pytest.param(
            {"history": {}},
            [("newfile.csv", "2021-01-05T00:00:00.000000Z")],
            ("newfile.csv", "2021-01-05T00:00:00.000000Z"),
            {"newfile.csv": "2021-01-05T00:00:00.000000Z"},
            [],
            "2021-01-05T00:00:00.000000Z_newfile.csv",
            id="add-to-empty-history-single-pending-file",
        ),
        pytest.param(
            {"history": {}},
            [("newfile.csv", "2021-01-05T00:00:00.000000Z"), ("pending.csv", "2020-01-05T00:00:00.000000Z")],
            ("newfile.csv", "2021-01-05T00:00:00.000000Z"),
            {"newfile.csv": "2021-01-05T00:00:00.000000Z"},
            [("pending.csv", "2020-01-05T00:00:00.000000Z")],
            "2020-01-05T00:00:00.000000Z_pending.csv",
            id="add-to-empty-history-pending-file-is-older",
        ),
        pytest.param(
            {"history": {}},
            [("newfile.csv", "2021-01-05T00:00:00.000000Z"), ("pending.csv", "2022-01-05T00:00:00.000000Z")],
            ("newfile.csv", "2021-01-05T00:00:00.000000Z"),
            {"newfile.csv": "2021-01-05T00:00:00.000000Z"},
            [("pending.csv", "2022-01-05T00:00:00.000000Z")],
            "2022-01-05T00:00:00.000000Z_pending.csv",
            id="add-to-empty-history-pending-file-is-newer",
        ),
        pytest.param(
            {"history": {"existing.csv": "2021-01-04T00:00:00.000000Z"}},
            [("newfile.csv", "2021-01-05T00:00:00.000000Z")],
            ("newfile.csv", "2021-01-05T00:00:00.000000Z"),
            {"existing.csv": "2021-01-04T00:00:00.000000Z", "newfile.csv": "2021-01-05T00:00:00.000000Z"},
            [],
            "2021-01-05T00:00:00.000000Z_newfile.csv",
            id="add-to-nonempty-history-single-pending-file",
        ),
        pytest.param(
            {"history": {"existing.csv": "2021-01-04T00:00:00.000000Z"}},
            [("newfile.csv", "2021-01-05T00:00:00.000000Z"), ("pending.csv", "2020-01-05T00:00:00.000000Z")],
            ("newfile.csv", "2021-01-05T00:00:00.000000Z"),
            {"existing.csv": "2021-01-04T00:00:00.000000Z", "newfile.csv": "2021-01-05T00:00:00.000000Z"},
            [("pending.csv", "2020-01-05T00:00:00.000000Z")],
            "2020-01-05T00:00:00.000000Z_pending.csv",
            id="add-to-nonempty-history-pending-file-is-older",
        ),
        pytest.param(
            {"history": {"existing.csv": "2021-01-04T00:00:00.000000Z"}},
            [("newfile.csv", "2021-01-05T00:00:00.000000Z"), ("pending.csv", "2022-01-05T00:00:00.000000Z")],
            ("newfile.csv", "2021-01-05T00:00:00.000000Z"),
            {"existing.csv": "2021-01-04T00:00:00.000000Z", "newfile.csv": "2021-01-05T00:00:00.000000Z"},
            [("pending.csv", "2022-01-05T00:00:00.000000Z")],
            "2022-01-05T00:00:00.000000Z_pending.csv",
            id="add-to-nonempty-history-pending-file-is-newer",
        ),
    ],
)
def test_add_file(
    initial_state: MutableMapping[str, Any],
    pending_files: List[Tuple[str, str]],
    file_to_add: Tuple[str, str],
    expected_history: Dict[str, Any],
    expected_pending_files: List[Tuple[str, str]],
    expected_cursor_value: str,
):
    cursor = _make_cursor(initial_state)
    mock_message_repository = MagicMock()
    cursor._message_repository = mock_message_repository
    stream = MagicMock()

    cursor.set_pending_partitions(
        [
            FileBasedStreamPartition(
                stream,
                {"files": [RemoteFile(uri=uri, last_modified=datetime.strptime(timestamp, DATE_TIME_FORMAT))]},
                mock_message_repository,
                SyncMode.full_refresh,
                FileBasedConcurrentCursor.CURSOR_FIELD,
                initial_state,
                cursor,
            )
            for uri, timestamp in pending_files
        ]
    )

    uri, timestamp = file_to_add
    cursor.add_file(RemoteFile(uri=uri, last_modified=datetime.strptime(timestamp, DATE_TIME_FORMAT)))
    assert cursor._file_to_datetime_history == expected_history
    assert cursor._pending_files == {
        uri: RemoteFile(uri=uri, last_modified=datetime.strptime(timestamp, DATE_TIME_FORMAT)) for uri, timestamp in expected_pending_files
    }
    assert (
        mock_message_repository.emit_message.call_args_list[0].args[0].state.stream.stream_state._ab_source_file_last_modified
        == expected_cursor_value
    )


@pytest.mark.parametrize(
    "initial_state, pending_files, file_to_add, expected_history, expected_pending_files, expected_cursor_value",
    [
        pytest.param(
            {"history": {}},
            [],
            ("newfile.csv", "2021-01-05T00:00:00.000000Z"),
            {"newfile.csv": "2021-01-05T00:00:00.000000Z"},
            [],
            "2021-01-05T00:00:00.000000Z_newfile.csv",
            id="add-to-empty-history-no-pending-files",
        ),
        pytest.param(
            {"history": {}},
            [("pending.csv", "2021-01-05T00:00:00.000000Z")],
            ("newfile.csv", "2021-01-05T00:00:00.000000Z"),
            {"newfile.csv": "2021-01-05T00:00:00.000000Z"},
            [("pending.csv", "2021-01-05T00:00:00.000000Z")],
            "2021-01-05T00:00:00.000000Z_pending.csv",
            id="add-to-empty-history-file-not-in-pending-files",
        ),
    ],
)
def test_add_file_invalid(
    initial_state: MutableMapping[str, Any],
    pending_files: List[Tuple[str, str]],
    file_to_add: Tuple[str, str],
    expected_history: Dict[str, Any],
    expected_pending_files: List[Tuple[str, str]],
    expected_cursor_value: str,
):
    cursor = _make_cursor(initial_state)
    cursor._pending_files = {
        uri: RemoteFile(uri=uri, last_modified=datetime.strptime(timestamp, DATE_TIME_FORMAT)) for uri, timestamp in pending_files
    }
    mock_message_repository = MagicMock()
    cursor._message_repository = mock_message_repository

    uri, timestamp = file_to_add
    cursor.add_file(RemoteFile(uri=uri, last_modified=datetime.strptime(timestamp, DATE_TIME_FORMAT)))
    assert cursor._file_to_datetime_history == expected_history
    assert cursor._pending_files == {
        uri: RemoteFile(uri=uri, last_modified=datetime.strptime(timestamp, DATE_TIME_FORMAT)) for uri, timestamp in expected_pending_files
    }
    assert mock_message_repository.emit_message.call_args_list[0].args[0].log.level.value == "WARN"
    assert (
        mock_message_repository.emit_message.call_args_list[1].args[0].state.stream.stream_state._ab_source_file_last_modified
        == expected_cursor_value
    )


@pytest.mark.parametrize(
    "input_state, pending_files, expected_cursor_value",
    [
        pytest.param({}, [], f"{datetime.min.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}_", id="no-state-no-pending"),
        pytest.param(
            {"history": {"a.csv": "2021-01-01T00:00:00.000000Z"}}, [], "2021-01-01T00:00:00.000000Z_a.csv", id="no-pending-with-history"
        ),
        pytest.param(
            {"history": {}}, [("b.csv", "2021-01-02T00:00:00.000000Z")], "2021-01-02T00:00:00.000000Z_b.csv", id="pending-no-history"
        ),
        pytest.param(
            {"history": {"a.csv": "2022-01-01T00:00:00.000000Z"}},
            [("b.csv", "2021-01-02T00:00:00.000000Z")],
            "2021-01-01T00:00:00.000000Z_a.csv",
            id="with-pending-before-history",
        ),
        pytest.param(
            {"history": {"a.csv": "2021-01-01T00:00:00.000000Z"}},
            [("b.csv", "2022-01-02T00:00:00.000000Z")],
            "2022-01-01T00:00:00.000000Z_a.csv",
            id="with-pending-after-history",
        ),
    ],
)
def test_get_new_cursor_value(input_state: MutableMapping[str, Any], pending_files: List[Tuple[str, str]], expected_cursor_value: str):
    cursor = _make_cursor(input_state)
    pending_partitions = []
    for url, timestamp in pending_files:
        partition = MagicMock()
        partition.to_slice = lambda *args, **kwargs: {
            "files": [RemoteFile(uri=url, last_modified=datetime.strptime(timestamp, DATE_TIME_FORMAT))]
        }
        pending_partitions.append(partition)

    cursor.set_pending_partitions(pending_partitions)


@pytest.mark.parametrize(
    "all_files, history, is_history_full, prev_cursor_value, expected_files_to_sync",
    [
        pytest.param(
            [RemoteFile(uri="new.csv", last_modified=datetime.strptime("2021-01-03T00:00:00.000000Z", "%Y-%m-%dT%H:%M:%S.%fZ"))],
            {},
            False,
            (datetime.min, ""),
            ["new.csv"],
            id="empty-history-one-new-file",
        ),
        pytest.param(
            [RemoteFile(uri="a.csv", last_modified=datetime.strptime("2021-01-02T00:00:00.000000Z", "%Y-%m-%dT%H:%M:%S.%fZ"))],
            {"a.csv": "2021-01-01T00:00:00.000000Z"},
            False,
            (datetime.min, ""),
            ["a.csv"],
            id="non-empty-history-file-in-history-modified",
        ),
        pytest.param(
            [RemoteFile(uri="a.csv", last_modified=datetime.strptime("2021-01-01T00:00:00.000000Z", "%Y-%m-%dT%H:%M:%S.%fZ"))],
            {"a.csv": "2021-01-01T00:00:00.000000Z"},
            False,
            (datetime.min, ""),
            [],
            id="non-empty-history-file-in-history-not-modified",
        ),
    ],
)
def test_get_files_to_sync(all_files, history, is_history_full, prev_cursor_value, expected_files_to_sync):
    cursor = _make_cursor({})
    cursor._file_to_datetime_history = history
    cursor._prev_cursor_value = prev_cursor_value
    cursor._is_history_full = MagicMock(return_value=is_history_full)
    files_to_sync = list(cursor.get_files_to_sync(all_files, MagicMock()))
    assert [f.uri for f in files_to_sync] == expected_files_to_sync


@freeze_time("2023-06-16T00:00:00Z")
@pytest.mark.parametrize(
    "file_to_check, history, is_history_full, prev_cursor_value, sync_start, expected_should_sync",
    [
        pytest.param(
            RemoteFile(uri="new.csv", last_modified=datetime.strptime("2021-01-03T00:00:00.000000Z", DATE_TIME_FORMAT)),
            {},
            False,
            (datetime.min, ""),
            datetime.min,
            True,
            id="file-not-in-history-not-full-old-cursor",
        ),
        pytest.param(
            RemoteFile(uri="new.csv", last_modified=datetime.strptime("2021-01-03T00:00:00.000000Z", DATE_TIME_FORMAT)),
            {},
            False,
            (datetime.strptime("2024-01-02T00:00:00.000000Z", DATE_TIME_FORMAT), ""),
            datetime.min,
            True,
            id="file-not-in-history-not-full-new-cursor",
        ),
        pytest.param(
            RemoteFile(uri="a.csv", last_modified=datetime.strptime("2021-01-01T00:00:00.000000Z", DATE_TIME_FORMAT)),
            {"a.csv": "2021-01-01T00:00:00.000000Z"},
            False,
            (datetime.min, ""),
            datetime.min,
            False,
            id="file-in-history-not-modified",
        ),
        pytest.param(
            RemoteFile(uri="a.csv", last_modified=datetime.strptime("2020-01-01T00:00:00.000000Z", DATE_TIME_FORMAT)),
            {"a.csv": "2021-01-01T00:00:00.000000Z"},
            False,
            (datetime.min, ""),
            datetime.min,
            False,
            id="file-in-history-modified-before",
        ),
        pytest.param(
            RemoteFile(uri="a.csv", last_modified=datetime.strptime("2022-01-01T00:00:00.000000Z", DATE_TIME_FORMAT)),
            {"a.csv": "2021-01-01T00:00:00.000000Z"},
            False,
            (datetime.min, ""),
            datetime.min,
            True,
            id="file-in-history-modified-after",
        ),
        pytest.param(
            RemoteFile(uri="new.csv", last_modified=datetime.strptime("2022-01-01T00:00:00.000000Z", DATE_TIME_FORMAT)),
            {},
            True,
            (datetime.strptime("2021-01-02T00:00:00.000000Z", DATE_TIME_FORMAT), "a.csv"),
            datetime.min,
            True,
            id="history-full-file-modified-after-cursor",
        ),
        pytest.param(
            RemoteFile(uri="new1.csv", last_modified=datetime.strptime("2021-01-01T00:00:00.000000Z", DATE_TIME_FORMAT)),
            {},
            True,
            (datetime.strptime("2021-01-01T00:00:00.000000Z", DATE_TIME_FORMAT), "new0.csv"),
            datetime.min,
            True,
            id="history-full-modified-eq-cursor-uri-gt",
        ),
        pytest.param(
            RemoteFile(uri="new0.csv", last_modified=datetime.strptime("2021-01-01T00:00:00.000000Z", DATE_TIME_FORMAT)),
            {},
            True,
            (datetime.strptime("2021-01-01T00:00:00.000000Z", DATE_TIME_FORMAT), "new1.csv"),
            datetime.min,
            False,
            id="history-full-modified-eq-cursor-uri-lt",
        ),
        pytest.param(
            RemoteFile(uri="new.csv", last_modified=datetime.strptime("2020-01-01T00:00:00.000000Z", DATE_TIME_FORMAT)),
            {},
            True,
            (datetime.strptime("2021-01-01T00:00:00.000000Z", DATE_TIME_FORMAT), "a.csv"),
            datetime.min,
            True,
            id="history-full-modified-before-cursor-and-after-sync-start",
        ),
        pytest.param(
            RemoteFile(uri="new.csv", last_modified=datetime.strptime("2021-01-01T00:00:00.000000Z", DATE_TIME_FORMAT)),
            {},
            True,
            (datetime.strptime("2022-01-01T00:00:00.000000Z", DATE_TIME_FORMAT), "a.csv"),
            datetime.strptime("2024-01-01T00:00:00.000000Z", DATE_TIME_FORMAT),
            False,
            id="history-full-modified-before-cursor-and-before-sync-start",
        ),
    ],
)
def test_should_sync_file(
    file_to_check: RemoteFile,
    history: Dict[str, Any],
    is_history_full: bool,
    prev_cursor_value: Tuple[datetime, str],
    sync_start: datetime,
    expected_should_sync: bool,
):
    cursor = _make_cursor({})
    cursor._file_to_datetime_history = history
    cursor._prev_cursor_value = prev_cursor_value
    cursor._sync_start = sync_start
    cursor._is_history_full = MagicMock(return_value=is_history_full)
    should_sync = cursor._should_sync_file(file_to_check, MagicMock())
    assert should_sync == expected_should_sync


@freeze_time("2023-06-16T00:00:00Z")
@pytest.mark.parametrize(
    "input_history, is_history_full, expected_start_time",
    [
        pytest.param({}, False, datetime.min, id="empty-history"),
        pytest.param(
            {"a.csv": "2021-01-01T00:00:00.000000Z"},
            False,
            datetime.strptime("2021-01-01T00:00:00.000000Z", DATE_TIME_FORMAT),
            id="non-full-history",
        ),
        pytest.param(
            {f"file{i}.csv": f"2021-01-0{i}T00:00:00.000000Z" for i in range(1, 4)},  # all before the time window
            True,
            datetime.strptime("2021-01-01T00:00:00.000000Z", DATE_TIME_FORMAT),  # Time window start time
            id="full-history-earliest-before-window",
        ),
        pytest.param(
            {f"file{i}.csv": f"2024-01-0{i}T00:00:00.000000Z" for i in range(1, 4)},  # all after the time window
            True,
            datetime.strptime("2023-06-13T00:00:00.000000Z", DATE_TIME_FORMAT),  # Earliest file time
            id="full-history-earliest-after-window",
        ),
    ],
)
def test_compute_start_time(input_history, is_history_full, expected_start_time, monkeypatch):
    cursor = _make_cursor({"history": input_history})
    cursor._file_to_datetime_history = input_history
    cursor._is_history_full = MagicMock(return_value=is_history_full)
    assert cursor._compute_start_time() == expected_start_time
