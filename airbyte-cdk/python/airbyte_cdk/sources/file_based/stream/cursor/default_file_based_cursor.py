#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timedelta
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.cursor.file_based_cursor import FileBasedCursor
from airbyte_cdk.sources.file_based.stream.file_based_stream_config import FileBasedStreamConfig

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
        self._history_is_partial = False
        self._logger = logger
        self._start_time = self._compute_start_time()

    def set_initial_state(self, value: Mapping[str, Any]):
        self._file_to_datetime_history = value.get("history", {})
        self._history_is_partial = value.get("history_is_partial", False)
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
            "history_is_partial": self._history_is_partial,
        }
        return state

    def is_history_partial(self):
        return self._history_is_partial

    def _should_sync_file(self, file: RemoteFile) -> bool:
        if file.uri in self._file_to_datetime_history:
            # If the file's uri is in the history, we should not sync the file
            return False
        elif self.is_history_partial():
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
        files_to_sync = [f for f in all_files if self._should_sync_file(f)]
        # If the size of the resulting history is > max history size, the next sync will not be able to use the history
        if len(files_to_sync) + len(self._file_to_datetime_history) > self._max_history_size:
            self._history_is_partial = True
            self._logger.warning(
                f"Found {len(files_to_sync)} files to sync, which is more than the max history size of {self._max_history_size}. "
                f"The next sync won't be able to use the history to filter out duplicate files. "
                f"It will instead use the time window of {self._time_window_if_history_is_full} to filter out files."
            )
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
