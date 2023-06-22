#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timedelta
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources.file_based.remote_file import RemoteFile

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class FileBasedCursor:
    def __init__(self, max_history_size: int, time_window_if_history_is_full: timedelta, logger: logging.Logger):
        self._file_to_datetime_history: Mapping[str:datetime] = {}
        self._max_history_size = max_history_size
        self._time_window_if_history_is_full = time_window_if_history_is_full
        self._logger = logger
        self._start_time = self._compute_start_time()

    def set_initial_state(self, value: Mapping[str, Any]):
        self._file_to_datetime_history = value.get("history", {})
        self._start_time = self._compute_start_time()

    def add_file(self, file: RemoteFile):
        self._file_to_datetime_history[file.uri] = file.last_modified.strftime(DATE_TIME_FORMAT)
        if len(self._file_to_datetime_history) > self._max_history_size:
            # Get the earliest file based on its last modified date and its uri
            oldest_file = self._get_earliest_file_and_datetime()[0]
            del self._file_to_datetime_history[oldest_file]

    def get_state(self):
        state = {
            "history": self._file_to_datetime_history,
        }
        return state

    def is_history_partial(self):
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
                # If the history is partial and the file's datetime is equal to the start time,
                # we should sync the file if its URI is greater than the earliest URI in the history.
                earliest_file_uri, earliest_datetime = self._get_earliest_file_and_datetime()
                earliest_datetime = datetime.strptime(earliest_datetime, DATE_TIME_FORMAT)
                return file.last_modified == earliest_datetime and file.uri > earliest_file_uri
        else:
            return True

    def get_files_to_sync(self, all_files: List[RemoteFile]):
        if self.is_history_partial():
            self._logger.warning(
                f"The state history is full. "
                f"This sync and future syncs won't be able to use the history to filter out duplicate files. "
                f"It will instead use the time window of {self._time_window_if_history_is_full} to filter out files."
            )
        files_to_sync = [f for f in all_files if self._should_sync_file(f)]
        # If the size of the resulting history is > max history size, the next sync will not be able to use the history
        return files_to_sync

    def get_start_time(self):
        return self._start_time

    def _get_earliest_file_and_datetime(self) -> Tuple[str, str]:
        return min(self._file_to_datetime_history.items(), key=lambda f: (f[1], f[0]))

    def _compute_start_time(self) -> datetime:
        if not self._file_to_datetime_history:
            return datetime.min
        else:
            earliest = min(self._file_to_datetime_history.values())
            earliest_dt = datetime.strptime(earliest, "%Y-%m-%dT%H:%M:%S.%fZ")
            if self.is_history_partial():
                time_window = datetime.now() - self._time_window_if_history_is_full
                earliest_dt = min(earliest_dt, time_window)
            return earliest_dt
