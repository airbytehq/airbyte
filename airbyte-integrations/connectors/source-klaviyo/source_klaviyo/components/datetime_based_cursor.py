#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


@dataclass
class KlaviyoDatetimeBasedCursor(DatetimeBasedCursor):
    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        if not stream_slice:
            return {}

        field = self.cursor_field.eval(self.config)
        value = stream_slice.get(self._partition_field_start.eval(self.config))
        return {"filter": f"greater-than({field},{value})", "sort": field}


@dataclass
class KlaviyoCheckpointDatetimeBasedCursor(DatetimeBasedCursor):
    """
    You can configure the declarative stream with a step to checkpoint after the slice is completed
    e.g.
        incremental_sync:
            type: CustomIncrementalSync
            ... some configuration
            step: P1M
            cursor_granularity: PT1S
    """

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        if not stream_slice:
            return {}

        field = self.cursor_field.eval(self.config)
        start_value = stream_slice.get(self._partition_field_start.eval(self.config))
        end_value = stream_slice.get(self._partition_field_end.eval(self.config))
        return {"filter": f"greater-or-equal({field},{start_value}),less-or-equal({field},{end_value})", "sort": field}
