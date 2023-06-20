#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timedelta
from typing import Any, List, Mapping

from airbyte_cdk.sources.file_based.remote_file import RemoteFile


class FileBasedState:
    def __init__(self, max_history_size: int, time_window_if_history_is_full: timedelta, logger: logging.Logger):
        self._file_to_datetime_history: Mapping[str:datetime] = {}
        self._max_history_size = max_history_size
        self._time_window_if_history_is_full = time_window_if_history_is_full
        self._history_is_partial = False
        self._logger = logger

    def set_initial_state(self, value: Mapping[str, Any]):
        self._file_to_datetime_history = value.get("history", {})
        self._history_is_partial = value.get("history_is_partial", False)

    def add_file(self, file: RemoteFile):
        self._file_to_datetime_history[file.uri] = file.last_modified.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if len(self._file_to_datetime_history) > self._max_history_size:
            oldest_file = min(self._file_to_datetime_history, key=self._file_to_datetime_history.get)
            del self._file_to_datetime_history[oldest_file]

    def to_dict(self):
        state = {
            "history": self._file_to_datetime_history,
            "history_is_partial": self._history_is_partial,
        }
        return state

    def is_history_partial(self):
        return self._history_is_partial

    def get_files_to_sync(self, all_files: List[RemoteFile]):
        start_time = self.compute_start_time()
        files_to_sync = [
            f
            for f in all_files
            if (
                f.last_modified >= start_time
                and (not self._file_to_datetime_history or self.is_history_partial() or f.uri not in self._file_to_datetime_history)
            )
        ]
        # If len(files_to_sync), the next sync will not be able to use the history
        if len(files_to_sync) > self._max_history_size:
            self._history_is_partial = True
            self._logger.warning(
                f"Found {len(files_to_sync)} files to sync, which is more than the max history size of {self._max_history_size}. The next sync won't be able to use the history to filter out duplicate files. "
                f"It will instead use the time window of {self._time_window_if_history_is_full} to filter out files."
            )
        else:
            self._history_is_partial = False
        return files_to_sync

    def compute_start_time(self) -> datetime:
        if not self._file_to_datetime_history:
            return datetime.min
        else:
            earliest = min(self._file_to_datetime_history.values())
            earliest_dt = datetime.strptime(earliest, "%Y-%m-%dT%H:%M:%S.%fZ")
            if self.is_history_partial():
                time_window = datetime.now() - self._time_window_if_history_is_full
                earliest_dt = min(earliest_dt, time_window)
            return earliest_dt
