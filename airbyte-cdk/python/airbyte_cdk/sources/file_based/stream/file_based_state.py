#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timedelta
from typing import Any, List, Mapping, Optional

from airbyte_cdk.sources.file_based.remote_file import RemoteFile


class FileBasedState:
    def __init__(self, max_history_size: int, time_window_if_history_is_full: timedelta):
        self._file_to_datetime_history: Mapping[str:datetime] = {}
        self._max_history_size = max_history_size
        self._time_window_if_history_is_full = time_window_if_history_is_full
        self._history_is_complete = True

    def set_initial_state(self, value: Mapping[str, Any]):
        self._file_to_datetime_history = value.get("history", {})
        self._history_is_complete = not value.get("incomplete_history", False)

    def add_file(self, file: RemoteFile):
        self._file_to_datetime_history[file.uri] = file.last_modified.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if len(self._file_to_datetime_history) > self._max_history_size:
            oldest_file = min(self._file_to_datetime_history, key=self._file_to_datetime_history.get)
            del self._file_to_datetime_history[oldest_file]

    def to_dict(self):
        state = {
            "history": self._file_to_datetime_history,
        }
        if not self.is_history_complete():
            state["incomplete_history"] = True
        return state

    def is_history_complete(self):
        return self._history_is_complete

    def get_files_to_sync(self, all_files: List[RemoteFile]):
        start_time = self.compute_start_time()
        files_to_sync = [
            f
            for f in all_files
            if (
                f.last_modified >= start_time
                and (not self._file_to_datetime_history or not self.is_history_complete() or f.uri not in self._file_to_datetime_history)
            )
        ]
        # If len(files_to_sync), the next sync will not be able to use the history
        if len(files_to_sync) > self._max_history_size:
            self._history_is_complete = False
        else:
            self._history_is_complete = True
        return files_to_sync

    def compute_start_time(self) -> datetime:
        if not self._file_to_datetime_history:
            return datetime.min
        else:
            earliest = min(self._file_to_datetime_history.values())
            earliest_dt = datetime.strptime(earliest, "%Y-%m-%dT%H:%M:%S.%fZ")
            if not self.is_history_complete():
                time_window = datetime.now() - self._time_window_if_history_is_full
                earliest_dt = min(earliest_dt, time_window)
            return earliest_dt
