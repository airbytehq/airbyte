# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping, MutableMapping, Optional

from airbyte_cdk.sources.declarative.incremental.datetime_based_cursor import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


class IncrementalSingleBodyFilterCursor(DatetimeBasedCursor):
    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_filter_options(RequestOptionType.body_json, stream_slice)

    def _get_request_filter_options(self, option_type: RequestOptionType, stream_slice: Optional[StreamSlice]) -> Mapping[str, Any]:
        options: MutableMapping[str, Any] = {}
        if not stream_slice:
            return options
        if self.start_time_option and self.start_time_option.inject_into == option_type:
            field_name, sub_field_name = self.start_time_option.field_name.eval(config=self.config).replace(" ", "").split(",")
            options[field_name] = {sub_field_name: stream_slice.get(self._partition_field_start.eval(self.config))}
        return options
