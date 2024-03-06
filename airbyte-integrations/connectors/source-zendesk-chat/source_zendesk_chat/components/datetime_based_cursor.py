#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


@dataclass
class ZendeskChatTimestampCursor(DatetimeBasedCursor):
    """
    Override for the default `DatetimeBasedCursor` to make self.close_slice() to produce the STATE from the RECORD cursor value instead of slicer values.
    The dates in future are not allowed for the Zendesk Chat endpoints, and slicer values could be far away from exact cursor values.

    Arguments:
        use_microseconds: bool - whether or not to add dummy `000000` (six zeros) to provide the microseconds unit timestamps
    """

    use_microseconds: Union[InterpolatedString, str] = True

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._use_microseconds = InterpolatedString.create(self.use_microseconds, parameters=parameters).eval(self.config)
        self._start_date = self.config.get("start_date")
        super().__post_init__(parameters=parameters)

    def close_slice(self, stream_slice: StreamSlice, most_recent_record: Optional[Record]) -> None:
        last_record_cursor_value = most_recent_record.get(self.cursor_field.eval(self.config)) if most_recent_record else None
        self._cursor = last_record_cursor_value if last_record_cursor_value else self._start_date

    def add_microseconds(
        self,
        field_name: str,
        params: MutableMapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> MutableMapping[str, Any]:
        start_time = stream_slice.get("start_time")
        if start_time:
            params["start_time"] = int(start_time) * 1000000
        return params

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        params = {}
        if self._use_microseconds:
            params = self.add_microseconds("start_time", params, stream_slice)
        else:
            params["start_time"] = stream_slice.get("start_time")
        return params
