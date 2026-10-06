#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timedelta
from typing import Any, MutableMapping

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamState


logger = logging.Logger("source-S3")


class Cursor(DefaultFileBasedCursor):
    _DATE_FORMAT = "%Y-%m-%d"
    _LEGACY_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    _V4_MIGRATION_BUFFER = timedelta(hours=1)
    _V3_MIN_SYNC_DATE_FIELD = "v3_min_sync_date"

    def __init__(self, stream_config: FileBasedStreamConfig, **_: Any):
        super().__init__(stream_config)
        self._running_migration = False
        self._v3_migration_start_datetime = None

    def set_initial_state(self, value: StreamState) -> None:
        if self._is_legacy_state(value):
            self._running_migration = True
            value = self._convert_legacy_state(value)
        else:
            self._running_migration = False
        self._v3_migration_start_datetime = (
            datetime.strptime(value.get(Cursor._V3_MIN_SYNC_DATE_FIELD), DefaultFileBasedCursor.DATE_TIME_FORMAT)
            if Cursor._V3_MIN_SYNC_DATE_FIELD in value
            else None
        )
        super().set_initial_state(value)

    def get_state(self) -> StreamState:
        state = {"history": self._file_to_datetime_history, self.CURSOR_FIELD: self._get_cursor()}
        if self._v3_migration_start_datetime:
            return {
                **state,
                **{
                    Cursor._V3_MIN_SYNC_DATE_FIELD: datetime.strftime(
                        self._v3_migration_start_datetime, DefaultFileBasedCursor.DATE_TIME_FORMAT
                    )
                },
            }
        else:
            return state

    def _should_sync_file(self, file: RemoteFile, logger: logging.Logger) -> bool:
        """
        Never sync files earlier than the v3 migration start date. V3 purged the history from the state, so we assume all files were already synced
        Else if the currenty sync is migrating from v3 to v4, sync all files that were modified within one hour of the last sync
        Else sync according to the default logic
        """
        if self._v3_migration_start_datetime and file.last_modified < self._v3_migration_start_datetime:
            return False
        elif self._running_migration:
            return True
        else:
            return super()._should_sync_file(file, logger)

    @staticmethod
    def _is_legacy_state(value: StreamState) -> bool:
        if not value:
            return False
        try:
            # Verify datetime format in history
            history = value.get("history", {}).keys()
            if history:
                item = list(value.get("history", {}).keys())[0]
                datetime.strptime(item, Cursor._DATE_FORMAT)

            # verify the format of the last_modified cursor
            last_modified_at_cursor = value.get(DefaultFileBasedCursor.CURSOR_FIELD)
            if not last_modified_at_cursor:
                return False
            datetime.strptime(last_modified_at_cursor, Cursor._LEGACY_DATE_TIME_FORMAT)
        except ValueError:
            return False
        return True

    @staticmethod
    def _convert_legacy_state(legacy_state: StreamState) -> MutableMapping[str, Any]:
        """
        Transform the history from the old state message format to the new.

        e.g.
        {
            "2022-05-26": ["simple_test.csv.csv", "simple_test_2.csv"],
            "2022-05-27": ["simple_test_2.csv", "redshift_result.csv"],
            ...
        }
        =>
        {
            "simple_test.csv": "2022-05-26T00:00:00.000000Z",
            "simple_test_2.csv": "2022-05-27T00:00:00.000000Z",
            "redshift_result.csv": "2022-05-27T00:00:00.000000Z",
            ...
        }
        """
        converted_history = {}
        legacy_cursor = legacy_state[DefaultFileBasedCursor.CURSOR_FIELD]
        cursor_datetime = datetime.strptime(legacy_cursor, Cursor._LEGACY_DATE_TIME_FORMAT)
        logger.info(f"Converting v3 -> v4 state. v3_cursor={legacy_cursor} v3_history={legacy_state.get('history')}")

        for date_str, filenames in legacy_state.get("history", {}).items():
            datetime_obj = Cursor._get_adjusted_date_timestamp(cursor_datetime, datetime.strptime(date_str, Cursor._DATE_FORMAT))

            for filename in filenames:
                if filename in converted_history:
                    if datetime_obj > datetime.strptime(
                        converted_history[filename],
                        DefaultFileBasedCursor.DATE_TIME_FORMAT,
                    ):
                        converted_history[filename] = datetime_obj.strftime(DefaultFileBasedCursor.DATE_TIME_FORMAT)
                    else:
                        # If the file was already synced with a later timestamp, ignore
                        pass
                else:
                    converted_history[filename] = datetime_obj.strftime(DefaultFileBasedCursor.DATE_TIME_FORMAT)

        if converted_history:
            filename, _ = max(converted_history.items(), key=lambda x: (x[1], x[0]))
            cursor = f"{cursor_datetime}_{filename}"
        else:
            # Having a cursor with empty history is not expected, but we handle it.
            logger.warning(f"Cursor found without a history object; this is not expected. cursor_value={legacy_cursor}")
            # Note: we convert to the v4 cursor granularity, but since no items are in the history we simply use the
            # timestamp as the cursor value instead of the concatenation of timestamp_filename, which is the v4
            # cursor format.
            # This is okay because the v4 cursor is kept for posterity but is not actually used in the v4 code. If we
            # start to use the cursor we may need to revisit this logic.
            cursor = cursor_datetime
            converted_history = {}
        v3_migration_start_datetime = cursor_datetime - Cursor._V4_MIGRATION_BUFFER
        return {
            "history": converted_history,
            DefaultFileBasedCursor.CURSOR_FIELD: cursor,
            Cursor._V3_MIN_SYNC_DATE_FIELD: v3_migration_start_datetime.strftime(DefaultFileBasedCursor.DATE_TIME_FORMAT),
        }

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
