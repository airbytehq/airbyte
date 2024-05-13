#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

import pendulum
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


class PinterestSemiIncrementalRecordFilter(RecordFilter):
    cursor_field = "updated_time"

    def filter_records(
        self,
        records: List[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> List[Mapping[str, Any]]:
        cursor_value = max(self._get_config_start_date(), self._get_current_partition_state(stream_state, stream_slice))
        return [record for record in records if record[self.cursor_field] >= cursor_value]

    def _get_config_start_date(self) -> int:
        start_date = self.config.get("start_date")
        return int(pendulum.parse(start_date).timestamp()) if start_date else 0

    def _get_current_partition_state(self, stream_state: StreamState, stream_slice: Optional[StreamSlice] = None) -> int:
        if not stream_slice:
            return 0

        current_partition_states = [
            state for state in stream_state.get("states", []) if state["partition"]["id"] == stream_slice.partition["id"]
        ]
        return current_partition_states[0]["cursor"][self.cursor_field] if current_partition_states else 0
