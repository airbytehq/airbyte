from datetime import datetime, timedelta
from typing import Mapping, Any, List, Optional

from airbyte_cdk.sources.file_based.remote_file import RemoteFile
import logging


class FileBasedState:
    def __init__(self, max_history_size: int, time_window_if_history_is_full: timedelta):
        self._state = {"history": {}}
        self._max_history_size = max_history_size
        logging.warning(f"max history size: {self._max_history_size}")
        self._time_window_if_history_is_full = time_window_if_history_is_full

    def set_initial_state(self, value: Mapping[str, Any]):
        self._state = value

    def add_file(self, file: RemoteFile):
        logging.warning(f"adding file to history: {file.uri}")
        self._state["history"][file.uri] = file.last_modified.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if len(self._state["history"]) > self._max_history_size:
            oldest_file = min(self._state["history"], key=self._state["history"].get)
            logging.warning(f"Removing {oldest_file} from history")
            del self._state["history"][oldest_file]

    def to_dict(self):
        return self._state

    def is_history_complete(self):
        return not self._state.get("incomplete_history", False)

    def get_files_to_sync(self, all_files: List[RemoteFile]):
        start_time = self.compute_start_time()
        files_to_sync = [f for f in all_files if
                         (f.last_modified >= start_time and
                          (not self._state or self._state.get("incomplete_history") or f.uri not in self._state["history"]))
                         ]
        logging.warning(f"files to sync: {files_to_sync}")
        # If len(files_to_sync), the next sync will not be able to use the history
        if len(files_to_sync) > self._max_history_size:
            logging.warning(f"History will be too large")
            self._state["incomplete_history"] = True
        else:
            self._state.pop("incomplete_history", None)
        return files_to_sync

    def compute_start_time(self) -> datetime:
        if not self._state or not self._state.get("history"):
            return datetime.min
        else:
            history = self._state.get("history", {})
            earliest = min(history.values())
            earliest_dt = datetime.strptime(earliest, "%Y-%m-%dT%H:%M:%S.%fZ")
            if self._state.get("incomplete_history"):
                logging.warning(f"History is incomplete")
                time_window = datetime.now() - self._time_window_if_history_is_full
                earliest_dt = min(earliest_dt, time_window)
            return earliest_dt
