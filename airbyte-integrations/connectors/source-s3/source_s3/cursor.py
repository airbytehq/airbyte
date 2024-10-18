#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timedelta
from typing import Any, MutableMapping

from airbyte_cdk import ConnectorStateManager, CursorField, MessageRepository
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.concurrent.cursor import FileBasedConcurrentCursor
from airbyte_cdk.sources.file_based.types import StreamState

logger = logging.Logger("source-S3")


class Cursor(FileBasedConcurrentCursor):
    _DATE_FORMAT = "%Y-%m-%d"
    _LEGACY_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    _V4_MIGRATION_BUFFER = timedelta(hours=1)
    _V3_MIN_SYNC_DATE_FIELD = "v3_min_sync_date"

    def __init__(
        self,
        stream_config: FileBasedStreamConfig,
        stream_name: str,
        stream_namespace: str | None,
        stream_state: MutableMapping[str, Any],
        message_repository: MessageRepository,
        connector_state_manager: ConnectorStateManager,
        cursor_field: CursorField,
    ) -> None:
        super().__init__(
            stream_config=stream_config,
            stream_name=stream_name,
            stream_namespace=stream_namespace,
            stream_state=stream_state,
            message_repository=message_repository,
            connector_state_manager=connector_state_manager,
            cursor_field=cursor_field,
        )
        self._running_migration = False
        self._v3_migration_start_datetime = None

    def set_initial_state(self, value: StreamState) -> None:
        self._v3_migration_start_datetime = (
            datetime.strptime(value.get(Cursor._V3_MIN_SYNC_DATE_FIELD), FileBasedConcurrentCursor.DATE_TIME_FORMAT)
            if Cursor._V3_MIN_SYNC_DATE_FIELD in value
            else None
        )
        super().set_initial_state(value)

    def get_state(self) -> StreamState:
        state = {"history": self._file_to_datetime_history, self.CURSOR_FIELD: self._get_new_cursor_value()}
        if self._v3_migration_start_datetime:
            return {
                **state,
                **{
                    Cursor._V3_MIN_SYNC_DATE_FIELD: datetime.strftime(
                        self._v3_migration_start_datetime, FileBasedConcurrentCursor.DATE_TIME_FORMAT
                    )
                },
            }
        else:
            return state

    def _should_sync_file(self, file: RemoteFile, logger: logging.Logger) -> bool:
        """
        Never sync files earlier than the v3 migration start date. V3 purged the history from the state, so we assume all files were already synced
        Else if the currently sync is migrating from v3 to v4, sync all files that were modified within one hour of the last sync
        Else sync according to the default logic
        """
        if self._v3_migration_start_datetime and file.last_modified < self._v3_migration_start_datetime:
            return False
        elif self._running_migration:
            return True
        else:
            return super()._should_sync_file(file, logger)

    @staticmethod
    def _get_adjusted_date_timestamp(cursor_datetime: datetime, file_datetime: datetime) -> datetime:
        if file_datetime > cursor_datetime:
            return file_datetime
        else:
            # Extract the dates so they can be compared
            cursor_date = cursor_datetime.date()
            date_obj = file_datetime.date()

            # If same day, update the time to the cursor time
            if date_obj == cursor_date:
                return file_datetime.replace(hour=cursor_datetime.hour, minute=cursor_datetime.minute, second=cursor_datetime.second)
            # If previous, update the time to end of day
            else:
                return file_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
