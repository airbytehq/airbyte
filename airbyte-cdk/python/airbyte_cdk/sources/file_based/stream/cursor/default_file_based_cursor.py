#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timedelta
from typing import Iterable, Mapping

from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.cursor.file_based_cursor import FileBasedCursor
from airbyte_cdk.sources.file_based.stream.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.types import StreamState

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class DefaultFileBasedCursor(FileBasedCursor):
    @staticmethod
    def create(stream_config: FileBasedStreamConfig, logger: logging.Logger):
        return DefaultFileBasedCursor(
            max_history_size=stream_config.max_history_size,
            time_window_if_history_is_full=timedelta(days=stream_config.days_to_sync_if_history_is_full)
            if stream_config.days_to_sync_if_history_is_full
            else None,
            logger=logger,
        )

    def __init__(self, max_history_size: int, time_window_if_history_is_full: timedelta, logger: logging.Logger):
        self._file_to_datetime_history: Mapping[str:datetime] = {}
        self._max_history_size = max_history_size or 10_000
        self._time_window_if_history_is_full = time_window_if_history_is_full or timedelta(days=3)
        self._logger = logger
        self._start_time = self._compute_start_time()

    def set_initial_state(self, value: StreamState) -> None:
        self._file_to_datetime_history = value.get("history", {})
        self._start_time = self._compute_start_time()
        self._initial_earliest_file_in_history = self._compute_earliest_file_in_history()

    def add_file(self, file: RemoteFile) -> None:
        self._file_to_datetime_history[file.uri] = file.last_modified.strftime(DATE_TIME_FORMAT)
        if len(self._file_to_datetime_history) > self._max_history_size:
            # Get the earliest file based on its last modified date and its uri
            oldest_file = self._compute_earliest_file_in_history()
            del self._file_to_datetime_history[oldest_file.uri]

    def get_state(self) -> StreamState:
        state = {
            "history": self._file_to_datetime_history,
        }
        return state

    def is_history_partial(self) -> bool:
        return len(self._file_to_datetime_history) >= self._max_history_size

    def _should_sync_file(self, file: RemoteFile) -> bool:
        if file.uri in self._file_to_datetime_history:
            # If the file's uri is in the history, we should sync the file if it has been modified since it was synced
            return file.last_modified > datetime.strptime(self._file_to_datetime_history.get(file.uri), DATE_TIME_FORMAT)
        if self.is_history_partial():
            if file.last_modified > self.get_start_time():
                # If the history is partial and the file's datetime is strictly greater than the start time, we should sync the file
                return True
            elif file.last_modified == self.get_start_time():
                # There are two scenarios to consider if last_modified == start_time
                # 1. last_modified == start_time == earliest datetime in the state's history
                # -> Only sync if the file is lexically greater than the earliest file in the state's history
                # 2. last_modified == start_time < earliest datetime in the state's history
                # -> Sync the file

                # Instead of computing the earliest file in the history again, we can use the one we computed when we set the initial state
                # since this method is only called at the start of a sync
                return file.last_modified < self._initial_earliest_file_in_history.last_modified or (
                    file.uri > self._initial_earliest_file_in_history.uri
                )
            else:  # file.last_modified < self.get_start_time()
                return False
        else:
            return True

    def get_files_to_sync(self, all_files: Iterable[RemoteFile]) -> Iterable[RemoteFile]:
        if self.is_history_partial():
            self._logger.warning(
                f"The state history is full. "
                f"This sync and future syncs won't be able to use the history to filter out duplicate files. "
                f"It will instead use the time window of {self._time_window_if_history_is_full} to filter out files."
            )
        for f in all_files:
            if self._should_sync_file(f):
                yield f

    def get_start_time(self) -> datetime:
        return self._start_time

    def _compute_earliest_file_in_history(self) -> RemoteFile:
        filename, last_modified = min(self._file_to_datetime_history.items(), key=lambda f: (f[1], f[0]))
        return RemoteFile(uri=filename, last_modified=datetime.strptime(last_modified, DATE_TIME_FORMAT))

    def _compute_start_time(self) -> datetime:
        if not self._file_to_datetime_history:
            return datetime.min
        else:
            earliest = min(self._file_to_datetime_history.values())
            earliest_dt = datetime.strptime(earliest, DATE_TIME_FORMAT)
            if self.is_history_partial():
                time_window = datetime.now() - self._time_window_if_history_is_full
                earliest_dt = min(earliest_dt, time_window)
            return earliest_dt
