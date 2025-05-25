# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse


@dataclass
class FreshcallerCallsIncrementalSync(DatetimeBasedCursor):
    """
    This class is created for Calls stream.

    According to the API docs, the endpoint is not configured for filtering using by_time[from] and by_time[to] parameters.
    Luckily it works when the parameters are specified. However, the filtering doesn't work as expected.
    Records with the specified by_time[from] are included which duplicates the record on successive reads.

    This custom component adds 1 microsecond to the start_time_value passed to the request_parameter to deduplicate records.
    """

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        options = super().get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        option_type = RequestOptionType.request_parameter

        if self.start_time_option and self.start_time_option.inject_into == option_type:
            start_time_value = stream_slice.get(self._partition_field_start.eval(self.config))
            start_time = ab_datetime_parse(start_time_value).add(timedelta(microseconds=1))
            self.start_time_option.inject_into_request(options, start_time, self.config)

        return options
