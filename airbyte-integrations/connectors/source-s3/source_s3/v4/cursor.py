#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import MutableMapping

from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamState


class Cursor(DefaultFileBasedCursor):
    DATE_FORMAT = "%Y-%m-%d"
    CURSOR_FIELD = "_ab_source_file_last_modified"

    def set_initial_state(self, value: StreamState) -> None:
        if self._is_legacy_state(value):
            value = self._convert_legacy_state(value)
        super().set_initial_state(value)

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

        for date_str, filenames in legacy_state.get("history", {}).items():
            date_obj = datetime.strptime(date_str, Cursor.DATE_FORMAT)

            for filename in filenames:
                if filename in converted_history:
                    if date_obj > datetime.strptime(converted_history[filename], DefaultFileBasedCursor.DATE_TIME_FORMAT):
                        converted_history[filename] = date_obj.strftime(DefaultFileBasedCursor.DATE_TIME_FORMAT)
                else:
                    converted_history[filename] = date_obj.strftime(DefaultFileBasedCursor.DATE_TIME_FORMAT)

        if converted_history:
            filename, timestamp = max(converted_history.items(), key=lambda x: (x[1], x[0]))
            cursor = f"{timestamp}_{filename}"
        else:
            cursor = None
        return {"history": converted_history, "_ab_source_file_last_modified": cursor}
