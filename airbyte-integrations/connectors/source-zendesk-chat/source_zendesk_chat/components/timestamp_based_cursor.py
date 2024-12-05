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
    Override for the default `DatetimeBasedCursor` to provide the `request_params["start_time"]` with added `microseconds`, as required by the API.
    More info: https://developer.zendesk.com/rest_api/docs/chat/incremental_export#incremental-agent-timeline-export

    The dates in future are not(!) allowed for the Zendesk Chat endpoints, and slicer values could be far away from exact cursor values.

    Arguments:
        use_microseconds: bool - whether or not to add dummy `000000` (six zeros) to provide the microseconds unit timestamps
    """

    use_microseconds: Union[InterpolatedString, str] = True

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._use_microseconds = InterpolatedString.create(self.use_microseconds, parameters=parameters).eval(self.config)
        self._start_date = self.config.get("start_date")
        super().__post_init__(parameters=parameters)

    def add_microseconds(
        self,
        params: MutableMapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> MutableMapping[str, Any]:
        start_time = stream_slice.get(self._partition_field_start.eval(self.config))
        if start_time:
            params[self.start_time_option.field_name.eval(config=self.config)] = int(start_time) * 1000000
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
            params = self.add_microseconds(params, stream_slice)
        else:
            params[self.start_time_option.field_name.eval(config=self.config)] = stream_slice.get(
                self._partition_field_start.eval(self.config)
            )
        return params
