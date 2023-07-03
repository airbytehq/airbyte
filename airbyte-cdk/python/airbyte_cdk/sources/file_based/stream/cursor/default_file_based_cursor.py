#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timedelta
from typing import Iterable, Mapping, Optional

from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.cursor.file_based_cursor import FileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamState


class DefaultFileBasedCursor(FileBasedCursor):
    DEFAULT_DAYS_TO_SYNC_IF_HISTORY_IS_FULL = 3
    DEFAULT_MAX_HISTORY_SIZE = 10_000
    DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(self, max_history_size: Optional[int], days_to_sync_if_history_is_full: Optional[int]):
        self._file_to_datetime_history: Mapping[str:datetime] = {}
        self._max_history_size = max_history_size or self.DEFAULT_MAX_HISTORY_SIZE
        self._time_window_if_history_is_full = timedelta(
            days=days_to_sync_if_history_is_full or self.DEFAULT_DAYS_TO_SYNC_IF_HISTORY_IS_FULL
        )

        if self._max_history_size <= 0:
            raise ValueError(f"max_history_size must be a positive integer, got {self._max_history_size}")
        if self._time_window_if_history_is_full <= timedelta():
            raise ValueError(f"days_to_sync_if_history_is_full must be a positive timedelta, got {self._time_window_if_history_is_full}")

        self._start_time = self._compute_start_time()
        self._initial_earliest_file_in_history: Optional[RemoteFile] = None

    def set_initial_state(self, value: StreamState) -> None:
        self._file_to_datetime_history = value.get("history", {})
        self._start_time = self._compute_start_time()
        self._initial_earliest_file_in_history = self._compute_earliest_file_in_history()

    def add_file(self, file: RemoteFile) -> None:
        self._file_to_datetime_history[file.uri] = file.last_modified.strftime(self.DATE_TIME_FORMAT)
        if len(self._file_to_datetime_history) > self._max_history_size:
            # Get the earliest file based on its last modified date and its uri
            oldest_file = self._compute_earliest_file_in_history()
            if oldest_file:
                del self._file_to_datetime_history[oldest_file.uri]
            else:
                raise Exception(
                    "The history is full but there is no files in the history. This should never happen and might be indicative of a bug in the CDK."
                )

    def get_state(self) -> StreamState:
        state = {
            "history": self._file_to_datetime_history,
        }
        return state

    def _is_history_full(self) -> bool:
        """
        Returns true if the state's history is full, meaning new entries will start to replace old entries.
        """
        return len(self._file_to_datetime_history) >= self._max_history_size

    def _should_sync_file(self, file: RemoteFile, logger: logging.Logger) -> bool:
        if file.uri in self._file_to_datetime_history:
            # If the file's uri is in the history, we should sync the file if it has been modified since it was synced
            updated_at_from_history = datetime.strptime(self._file_to_datetime_history.get(file.uri), self.DATE_TIME_FORMAT)
            if file.last_modified < updated_at_from_history:
                logger.warning(
                    f"The file {file.uri}'s last modified date is older than the last time it was synced. This is unexpected. Skipping the file."
                )
            else:
                return file.last_modified > updated_at_from_history
            return file.last_modified > updated_at_from_history
        if self._is_history_full():
            if file.last_modified > self._initial_earliest_file_in_history.last_modified:
                # If the history is partial and the file's datetime is strictly greater than the earliest file in the history,
                # we should sync it
                return True
            elif file.last_modified == self._initial_earliest_file_in_history.last_modified:
                # If the history is partial and the file's datetime is equal to the earliest file in the history,
                # we should sync it if its uri is strictly greater than the earliest file in the history
                return file.uri > self._initial_earliest_file_in_history.uri
            else:
                # Otherwise, only sync the file if it has been modified since the start of the time window
                return file.last_modified >= self.get_start_time()
        else:
            # The file is not in the history and the history is complete. We know we need to sync the file
            return True

    def get_files_to_sync(self, all_files: Iterable[RemoteFile], logger: logging.Logger) -> Iterable[RemoteFile]:
        if self._is_history_full():
            logger.warning(
                f"The state history is full. "
                f"This sync and future syncs won't be able to use the history to filter out duplicate files. "
                f"It will instead use the time window of {self._time_window_if_history_is_full} to filter out files."
            )
        for f in all_files:
            if self._should_sync_file(f, logger):
                yield f

    def get_start_time(self) -> datetime:
        return self._start_time

    def _compute_earliest_file_in_history(self) -> Optional[RemoteFile]:
        if self._file_to_datetime_history:
            filename, last_modified = min(self._file_to_datetime_history.items(), key=lambda f: (f[1], f[0]))
            return RemoteFile(uri=filename, last_modified=datetime.strptime(last_modified, self.DATE_TIME_FORMAT))
        else:
            return None

    def _compute_start_time(self) -> datetime:
        if not self._file_to_datetime_history:
            return datetime.min
        else:
            earliest = min(self._file_to_datetime_history.values())
            earliest_dt = datetime.strptime(earliest, self.DATE_TIME_FORMAT)
            if self._is_history_full():
                time_window = datetime.now() - self._time_window_if_history_is_full
                earliest_dt = min(earliest_dt, time_window)
            return earliest_dt
