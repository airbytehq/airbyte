#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from datetime import datetime, timedelta
from typing import Any, MutableMapping

from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamState


class Cursor(DefaultFileBasedCursor):
    _DATE_FORMAT = "%Y-%m-%d"
    _LEGACY_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    _V4_MIGRATION_BUFFER = timedelta(hours=1)

    def set_initial_state(self, value: StreamState) -> None:
        if self._is_legacy_state(value):
            value = self._convert_legacy_state(value)
        self._v3_migration_start_datetime = value.get("v3_migration_start_datetime", None)
        super().set_initial_state(value)

    def _should_sync_file(self, file: RemoteFile, logger: logging.Logger) -> bool:
        # When upgrading from v3 to v4, we want to sync all files that were modified within one hour of the last sync
        if self._v3_migration_start_datetime:
            return file.last_modified >= self._v3_migration_start_datetime
        else:
            return super()._should_sync_file(file, logger)

    @staticmethod
    def _is_legacy_state(value: StreamState) -> bool:
        if not value:
            return False
        try:
            # Verify datetime format in history
            item = list(value.get("history", {}).keys())[0]
            datetime.strptime(item, Cursor._DATE_FORMAT)

            # verify the format of the last_modified cursor
            last_modified_at_cursor = value.get(DefaultFileBasedCursor.CURSOR_FIELD)
            if not last_modified_at_cursor:
                return False
            datetime.strptime(last_modified_at_cursor, Cursor._LEGACY_DATE_TIME_FORMAT)
        except (IndexError, ValueError):
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

        cursor_datetime = datetime.strptime(legacy_state[DefaultFileBasedCursor.CURSOR_FIELD], Cursor._LEGACY_DATE_TIME_FORMAT)
        for date_str, filenames in legacy_state.get("history", {}).items():
            datetime_obj = Cursor._get_adjusted_date_timestamp(cursor_datetime, datetime.strptime(date_str, Cursor._DATE_FORMAT))

            for filename in filenames:
                if filename in converted_history:
                    if datetime_obj > datetime.strptime(converted_history[filename], DefaultFileBasedCursor.DATE_TIME_FORMAT):
                        converted_history[filename] = datetime_obj.strftime(DefaultFileBasedCursor.DATE_TIME_FORMAT)
                    else:
                        # If the file was already synced with a later timestamp, ignore
                        pass
                else:
                    converted_history[filename] = datetime_obj.strftime(DefaultFileBasedCursor.DATE_TIME_FORMAT)

        if converted_history:
            filename, _ = max(converted_history.items(), key=lambda x: (x[1], x[0]))
            cursor = f"{cursor_datetime}_{filename}"
            v3_migration_start_datetime = cursor_datetime - Cursor._V4_MIGRATION_BUFFER
        else:
            # If there is no history, _is_legacy_state should return False, so we should never get here
            raise ValueError("No history found in state message. Please contact support.")
        return {
            "history": converted_history,
            DefaultFileBasedCursor.CURSOR_FIELD: cursor,
            "v3_migration_start_datetime": v3_migration_start_datetime,
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
