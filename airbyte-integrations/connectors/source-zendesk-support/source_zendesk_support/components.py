# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional

from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState

@dataclass
class ZendeskSupportAuditLogsIncrementalSync(DatetimeBasedCursor):
    """
    This class is created for the Audit Logs stream. List with time range is used for record filtering.
    """
    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        option_type = RequestOptionType.request_parameter
        options: MutableMapping[str, Any] = {}
        if not stream_slice:
            return options

        # set list with time range
        if self.start_time_option and self.start_time_option.inject_into == option_type:
            start_time = stream_slice.get(self._partition_field_start.eval(self.config))
            options[self.start_time_option.field_name.eval(config=self.config)] = [start_time]  # type: ignore # field_name is always casted to an interpolated string
        if self.end_time_option and self.end_time_option.inject_into == option_type:
            options[self.end_time_option.field_name.eval(config=self.config)].append(stream_slice.get(self._partition_field_end.eval(self.config)))  # type: ignore # field_name is always casted to an interpolated string
        return options
