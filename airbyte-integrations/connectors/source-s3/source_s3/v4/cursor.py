#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from datetime import datetime, timedelta
from typing import MutableMapping
from zoneinfo import ZoneInfo

from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamState


class Cursor(DefaultFileBasedCursor):
    DATE_FORMAT = "%Y-%m-%d"
    LEGACY_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    CURSOR_FIELD = "_ab_source_file_last_modified"

    def set_initial_state(self, value: StreamState) -> None:
        if self._is_legacy_state(value):
            value = self._convert_legacy_state(value)
            self._v3_min_sync_dt = value.get("v3_min_sync_dt", False)
        super().set_initial_state(value)

    def _should_sync_file(self, file: RemoteFile, logger: logging.Logger) -> bool:
        if self._v3_min_sync_dt:
            return file.last_modified >= self._v3_min_sync_dt
        else:
            return self.super()._should_sync_file(file, logger)

    @staticmethod
    def _is_legacy_state(value: StreamState) -> bool:
        if not value:
            return False
        item = list(value.get("history", {}).keys())[0]
        try:
            datetime.strptime(item, Cursor.DATE_FORMAT)
        except ValueError:
            return False
        return True

    @staticmethod
    def _convert_legacy_state(legacy_state: StreamState) -> MutableMapping[str, str]:
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

        timestamp = datetime.strptime(legacy_state["_ab_source_file_last_modified"], Cursor.LEGACY_DATE_TIME_FORMAT)
        for date_str, filenames in legacy_state.get("history", {}).items():
            datetime_obj = datetime.strptime(date_str, Cursor.DATE_FORMAT)
            datetime_obj = Cursor._get_adjusted_date_timestamp(timestamp, datetime_obj)

            for filename in filenames:
                if filename in converted_history:
                    if datetime_obj > datetime.strptime(converted_history[filename], DefaultFileBasedCursor.DATE_TIME_FORMAT):
                        converted_history[filename] = datetime_obj.strftime(DefaultFileBasedCursor.DATE_TIME_FORMAT)
                else:
                    converted_history[filename] = datetime_obj.strftime(DefaultFileBasedCursor.DATE_TIME_FORMAT)

        if converted_history:
            filename, _ = max(converted_history.items(), key=lambda x: (x[1], x[0]))
            cursor = f"{timestamp}_{filename}"
            v3_min_sync_dt = timestamp.replace(tzinfo=ZoneInfo("UTC")) - timedelta(hours=1)
        else:
            cursor = None
            # FIXME: Set a default v3_min_
        return {"history": converted_history, "_ab_source_file_last_modified": cursor, "v3_min_sync_dt": v3_min_sync_dt}

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
