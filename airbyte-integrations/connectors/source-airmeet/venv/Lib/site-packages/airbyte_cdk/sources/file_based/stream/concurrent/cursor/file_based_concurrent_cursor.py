#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timedelta
from threading import RLock
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, MutableMapping, Optional, Tuple

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, Type
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.concurrent.cursor.abstract_concurrent_file_based_cursor import (
    AbstractConcurrentFileBasedCursor,
)
from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamState
from airbyte_cdk.sources.message.repository import MessageRepository
from airbyte_cdk.sources.streams.concurrent.cursor import CursorField
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.types import Record

if TYPE_CHECKING:
    from airbyte_cdk.sources.file_based.stream.concurrent.adapters import FileBasedStreamPartition

_NULL_FILE = ""


class FileBasedConcurrentCursor(AbstractConcurrentFileBasedCursor):
    CURSOR_FIELD = "_ab_source_file_last_modified"
    DEFAULT_DAYS_TO_SYNC_IF_HISTORY_IS_FULL = (
        DefaultFileBasedCursor.DEFAULT_DAYS_TO_SYNC_IF_HISTORY_IS_FULL
    )
    DEFAULT_MAX_HISTORY_SIZE = 10_000
    DATE_TIME_FORMAT = DefaultFileBasedCursor.DATE_TIME_FORMAT
    zero_value = datetime.min
    zero_cursor_value = f"0001-01-01T00:00:00.000000Z_{_NULL_FILE}"

    def __init__(
        self,
        stream_config: FileBasedStreamConfig,
        stream_name: str,
        stream_namespace: Optional[str],
        stream_state: MutableMapping[str, Any],
        message_repository: MessageRepository,
        connector_state_manager: ConnectorStateManager,
        cursor_field: CursorField,
    ) -> None:
        super().__init__()
        self._stream_name = stream_name
        self._stream_namespace = stream_namespace
        self._state = stream_state
        self._message_repository = message_repository
        self._connector_state_manager = connector_state_manager
        self._cursor_field = cursor_field
        self._time_window_if_history_is_full = timedelta(
            days=stream_config.days_to_sync_if_history_is_full
            or self.DEFAULT_DAYS_TO_SYNC_IF_HISTORY_IS_FULL
        )
        self._state_lock = RLock()
        self._pending_files_lock = RLock()
        self._pending_files: Optional[Dict[str, RemoteFile]] = None
        self._file_to_datetime_history = stream_state.get("history", {}) if stream_state else {}
        self._prev_cursor_value = self._compute_prev_sync_cursor(stream_state)
        self._sync_start = self._compute_start_time()

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    def observe(self, record: Record) -> None:
        pass

    def close_partition(self, partition: Partition) -> None:
        with self._pending_files_lock:
            if self._pending_files is None:
                raise RuntimeError(
                    "Expected pending partitions to be set but it was not. This is unexpected. Please contact Support."
                )

    def set_pending_partitions(self, partitions: List["FileBasedStreamPartition"]) -> None:
        with self._pending_files_lock:
            self._pending_files = {}
            for partition in partitions:
                _slice = partition.to_slice()
                if _slice is None:
                    continue
                for file in _slice["files"]:
                    if file.uri in self._pending_files.keys():
                        raise RuntimeError(
                            f"Already found file {_slice} in pending files. This is unexpected. Please contact Support."
                        )
                self._pending_files.update({file.uri: file})

    def _compute_prev_sync_cursor(self, value: Optional[StreamState]) -> Tuple[datetime, str]:
        if not value:
            return self.zero_value, ""
        prev_cursor_str = value.get(self._cursor_field.cursor_field_key) or self.zero_cursor_value
        # So if we see a cursor greater than the earliest file, it means that we have likely synced all files.
        # However, we take the earliest file as the cursor value for the purpose of checking which files to
        # sync, in case new files have been uploaded in the meantime.
        # This should be very rare, as it would indicate a race condition where a file with an earlier
        # last_modified time was uploaded after a file with a later last_modified time. Since last_modified
        # represents the start time that the file was uploaded, we can usually expect that all previous
        # files have already been uploaded. If that's the case, they'll be in history and we'll skip
        # re-uploading them.
        earliest_file_cursor_value = self._get_cursor_key_from_file(
            self._compute_earliest_file_in_history()
        )
        cursor_str = min(prev_cursor_str, earliest_file_cursor_value)
        cursor_dt, cursor_uri = cursor_str.split("_", 1)
        return datetime.strptime(cursor_dt, self.DATE_TIME_FORMAT), cursor_uri

    def _get_cursor_key_from_file(self, file: Optional[RemoteFile]) -> str:
        if file:
            return f"{datetime.strftime(file.last_modified, self.DATE_TIME_FORMAT)}_{file.uri}"
        return self.zero_cursor_value

    def _compute_earliest_file_in_history(self) -> Optional[RemoteFile]:
        with self._state_lock:
            if self._file_to_datetime_history:
                filename, last_modified = min(
                    self._file_to_datetime_history.items(), key=lambda f: (f[1], f[0])
                )
                return RemoteFile(
                    uri=filename,
                    last_modified=datetime.strptime(last_modified, self.DATE_TIME_FORMAT),
                )
            else:
                return None

    def add_file(self, file: RemoteFile) -> None:
        """
        Add a file to the cursor. This method is called when a file is processed by the stream.
        :param file: The file to add
        """
        if self._pending_files is None:
            raise RuntimeError(
                "Expected pending partitions to be set but it was not. This is unexpected. Please contact Support."
            )
        with self._pending_files_lock:
            with self._state_lock:
                if file.uri not in self._pending_files:
                    self._message_repository.emit_message(
                        AirbyteMessage(
                            type=Type.LOG,
                            log=AirbyteLogMessage(
                                level=Level.WARN,
                                message=f"The file {file.uri} was not found in the list of pending files. This is unexpected. Please contact Support",
                            ),
                        )
                    )
                else:
                    self._pending_files.pop(file.uri)
                self._file_to_datetime_history[file.uri] = file.last_modified.strftime(
                    self.DATE_TIME_FORMAT
                )
                if len(self._file_to_datetime_history) > self.DEFAULT_MAX_HISTORY_SIZE:
                    # Get the earliest file based on its last modified date and its uri
                    oldest_file = self._compute_earliest_file_in_history()
                    if oldest_file:
                        del self._file_to_datetime_history[oldest_file.uri]
                    else:
                        raise Exception(
                            "The history is full but there is no files in the history. This should never happen and might be indicative of a bug in the CDK."
                        )
                self.emit_state_message()

    def emit_state_message(self) -> None:
        with self._state_lock:
            new_state = self.get_state()
            self._connector_state_manager.update_state_for_stream(
                self._stream_name,
                self._stream_namespace,
                new_state,
            )
            state_message = self._connector_state_manager.create_state_message(
                self._stream_name, self._stream_namespace
            )
            self._message_repository.emit_message(state_message)

    def _get_new_cursor_value(self) -> str:
        with self._pending_files_lock:
            with self._state_lock:
                if self._pending_files:
                    # If there are partitions that haven't been synced, we don't know whether the files that have been synced
                    # represent a contiguous region.
                    # To avoid missing files, we only increment the cursor up to the oldest pending file, because we know
                    # that all older files have been synced.
                    return self._get_cursor_key_from_file(self._compute_earliest_pending_file())
                elif self._file_to_datetime_history:
                    # If all partitions have been synced, we know that the sync is up-to-date and so can advance
                    # the cursor to the newest file in history.
                    return self._get_cursor_key_from_file(self._compute_latest_file_in_history())
                else:
                    return f"{self.zero_value.strftime(self.DATE_TIME_FORMAT)}_"

    def _compute_earliest_pending_file(self) -> Optional[RemoteFile]:
        if self._pending_files:
            return min(self._pending_files.values(), key=lambda x: x.last_modified)
        else:
            return None

    def _compute_latest_file_in_history(self) -> Optional[RemoteFile]:
        with self._state_lock:
            if self._file_to_datetime_history:
                filename, last_modified = max(
                    self._file_to_datetime_history.items(), key=lambda f: (f[1], f[0])
                )
                return RemoteFile(
                    uri=filename,
                    last_modified=datetime.strptime(last_modified, self.DATE_TIME_FORMAT),
                )
            else:
                return None

    def get_files_to_sync(
        self, all_files: Iterable[RemoteFile], logger: logging.Logger
    ) -> Iterable[RemoteFile]:
        """
        Given the list of files in the source, return the files that should be synced.
        :param all_files: All files in the source
        :param logger:
        :return: The files that should be synced
        """
        with self._state_lock:
            if self._is_history_full():
                logger.warning(
                    f"The state history is full. "
                    f"This sync and future syncs won't be able to use the history to filter out duplicate files. "
                    f"It will instead use the time window of {self._time_window_if_history_is_full} to filter out files."
                )
            for f in all_files:
                if self._should_sync_file(f, logger):
                    yield f

    def _should_sync_file(self, file: RemoteFile, logger: logging.Logger) -> bool:
        with self._state_lock:
            if file.uri in self._file_to_datetime_history:
                # If the file's uri is in the history, we should sync the file if it has been modified since it was synced
                updated_at_from_history = datetime.strptime(
                    self._file_to_datetime_history[file.uri], self.DATE_TIME_FORMAT
                )
                if file.last_modified < updated_at_from_history:
                    self._message_repository.emit_message(
                        AirbyteMessage(
                            type=Type.LOG,
                            log=AirbyteLogMessage(
                                level=Level.WARN,
                                message=f"The file {file.uri}'s last modified date is older than the last time it was synced. This is unexpected. Skipping the file.",
                            ),
                        )
                    )
                    return False
                else:
                    return file.last_modified > updated_at_from_history

            prev_cursor_timestamp, prev_cursor_uri = self._prev_cursor_value
            if self._is_history_full():
                if file.last_modified > prev_cursor_timestamp:
                    # If the history is partial and the file's datetime is strictly greater than the cursor, we should sync it
                    return True
                elif file.last_modified == prev_cursor_timestamp:
                    # If the history is partial and the file's datetime is equal to the earliest file in the history,
                    # we should sync it if its uri is greater than or equal to the cursor value.
                    return file.uri > prev_cursor_uri
                else:
                    return file.last_modified >= self._sync_start
            else:
                # The file is not in the history and the history is complete. We know we need to sync the file
                return True

    def _is_history_full(self) -> bool:
        """
        Returns true if the state's history is full, meaning new entries will start to replace old entries.
        """
        with self._state_lock:
            if self._file_to_datetime_history is None:
                raise RuntimeError(
                    "The history object has not been set. This is unexpected. Please contact Support."
                )
            return len(self._file_to_datetime_history) >= self.DEFAULT_MAX_HISTORY_SIZE

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

    def get_start_time(self) -> datetime:
        return self._sync_start

    def get_state(self) -> MutableMapping[str, Any]:
        """
        Get the state of the cursor.
        """
        with self._state_lock:
            return {
                "history": self._file_to_datetime_history,
                self._cursor_field.cursor_field_key: self._get_new_cursor_value(),
            }

    def set_initial_state(self, value: StreamState) -> None:
        pass

    def ensure_at_least_one_state_emitted(self) -> None:
        self.emit_state_message()

    def should_be_synced(self, record: Record) -> bool:
        return True
