# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
    RequestInput,
)
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState

@dataclass
class ZendeskSupportAuditLogsIncrementalSync(DatetimeBasedCursor):
    """
    This class is created for Tickets stream. When paginator hit the page limit it will return latest record cursor as next_page_token
    Request parameters will be updated with the next_page_token to continue iterating over results
    """
    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # _get_request_options is modified to return updated cursor filter if exist
        option_type = RequestOptionType.request_parameter
        options: MutableMapping[str, Any] = {}
        if not stream_slice:
            return options

        if self.start_time_option and self.start_time_option.inject_into == option_type:
            start_time = stream_slice.get(self._partition_field_start.eval(self.config))
            options[self.start_time_option.field_name.eval(config=self.config)] = [start_time]  # type: ignore # field_name is always casted to an interpolated string
        if self.end_time_option and self.end_time_option.inject_into == option_type:
            options[self.end_time_option.field_name.eval(config=self.config)].append(stream_slice.get(self._partition_field_end.eval(self.config)))  # type: ignore # field_name is always casted to an interpolated string
        return options


@dataclass
class ZendeskSupportArticlesIncrementalSync(DatetimeBasedCursor):
    """
    This class is created for Tickets stream. When paginator hit the page limit it will return latest record cursor as next_page_token
    Request parameters will be updated with the next_page_token to continue iterating over results
    """
    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        print(f"{next_page_token=}")
        # _get_request_options is modified to return updated cursor filter if exist
        options: MutableMapping[str, Any] = {}
        if not stream_slice or next_page_token:
            return options

        return super().get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
