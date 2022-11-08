#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
from typing import Any, Dict, Iterable, List, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from source_smartsheets.sheet import SmartSheetAPIWrapper


class SmartsheetStream(Stream):
    cursor_field = "modifiedAt"

    def __init__(self, smartsheet: SmartSheetAPIWrapper, config: Mapping[str, Any]):
        self.smartsheet = smartsheet
        self._state = {}
        self._config = config
        self._start_datetime = self._config.get("start_datetime") or "2020-01-01T00:00:00+00:00"

    @property
    def primary_key(self) -> str:
        return self.smartsheet.primary_key

    def get_json_schema(self) -> Dict[str, Any]:
        return self.smartsheet.json_schema

    @property
    def name(self) -> str:
        return self.smartsheet.name

    @property
    def state(self) -> Mapping[str, Any]:
        if not self._state:
            self._state = {self.cursor_field: self._start_datetime}
        return self._state

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state = value

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        def iso_dt(src):
            return datetime.datetime.fromisoformat(src)

        for record in self.smartsheet.read_records(self.state[self.cursor_field]):
            current_cursor_value = iso_dt(self.state[self.cursor_field])
            latest_cursor_value = iso_dt(record[self.cursor_field])
            new_cursor_value = max(latest_cursor_value, current_cursor_value)
            self.state = {self.cursor_field: new_cursor_value.isoformat("T", "seconds")}
            yield record
