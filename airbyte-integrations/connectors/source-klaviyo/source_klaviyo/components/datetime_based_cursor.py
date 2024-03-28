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

        field = self._cursor_field.eval(self.config)
        value = stream_slice.get(self._partition_field_start.eval(self.config))
        return {"filter": f"greater-than({field},{value})", "sort": field}
