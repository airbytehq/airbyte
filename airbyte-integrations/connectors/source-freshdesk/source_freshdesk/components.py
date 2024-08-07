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
from source_freshdesk.utils import CallCredit


@dataclass
class FreshdeskRequester(HttpRequester):
    """
    This class is created to add call throttling using the optional requests_per_minute parameter
    """

    request_body_json: Optional[RequestInput] = None
    request_headers: Optional[RequestInput] = None
    request_parameters: Optional[RequestInput] = None
    request_body_data: Optional[RequestInput] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        requests_per_minute = self.config.get("requests_per_minute")
        self._call_credit = CallCredit(balance=requests_per_minute) if requests_per_minute else None

        self.request_options_provider = InterpolatedRequestOptionsProvider(
            request_body_data=self.request_body_data,
            request_body_json=self.request_body_json,
            request_headers=self.request_headers,
            request_parameters=self.request_parameters,
            config=self.config,
            parameters=parameters or {},
        )
        super().__post_init__(parameters)

    def _consume_credit(self, credit):
        """Consume call credit, if there is no credit left within current window will sleep til next period"""
        if self._call_credit:
            self._call_credit.consume(credit)

    def send_request(
        self,
        **kwargs,
    ) -> Optional[requests.Response]:
        call_credit_cost = kwargs.pop("call_credit_cost", 1)
        self._consume_credit(call_credit_cost)
        return super().send_request(**kwargs)


@dataclass
class FreshdeskTicketsIncrementalRequester(FreshdeskRequester):
    """
    This class is created for the Tickets stream to modify parameters produced by stream slicer and paginator
    When the paginator hit the page limit it will return the latest record cursor for the next_page_token
    next_page_token will be used in the stream slicer to get updated cursor filter
    """

    def send_request(
        self,
        **kwargs,
    ) -> Optional[requests.Response]:
        # pagination strategy returns cursor_filter based on the latest record instead of page when the page limit is hit
        if type(kwargs["request_params"].get("page")) == str:
            kwargs["request_params"].pop("page")
        # set correct call credit cost for Tickets stream
        kwargs["call_credit_cost"] = 3
        return super().send_request(**kwargs)


@dataclass
class FreshdeskTicketsIncrementalSync(DatetimeBasedCursor):
    """
    This class is created for Tickets stream. When paginator hit the page limit it will return latest record cursor as next_page_token
    Request parameters will be updated with the next_page_token to continue iterating over results
    """

    def __post_init__(self, parameters: Mapping[str, Any]):
        super().__post_init__(parameters=parameters)
        self.updated_slice = None

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # if next_page_token is str it is the latest record cursor from the paginator that will be used for updated cursor filter
        # if next_page_token is int it is the page number
        next_page_token = next_page_token.get("next_page_token") if next_page_token else None
        if type(next_page_token) == str:
            self.updated_slice = next_page_token

        # _get_request_options is modified to return updated cursor filter if exist
        option_type = RequestOptionType.request_parameter
        options: MutableMapping[str, Any] = {}
        if not stream_slice:
            return options

        if self.start_time_option and self.start_time_option.inject_into == option_type:
            start_time = stream_slice.get(self._partition_field_start.eval(self.config)) if not self.updated_slice else self.updated_slice
            options[self.start_time_option.field_name.eval(config=self.config)] = start_time  # type: ignore # field_name is always casted to an interpolated string
        if self.end_time_option and self.end_time_option.inject_into == option_type:
            options[self.end_time_option.field_name.eval(config=self.config)] = stream_slice.get(self._partition_field_end.eval(self.config))  # type: ignore # field_name is always casted to an interpolated string
        return options


@dataclass
class FreshdeskTicketsPaginationStrategy(PageIncrement):
    """
    This pagination strategy will return latest record cursor for the next_page_token after hitting page count limit
    """

    PAGE_LIMIT = 300

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        # Stop paginating when there are fewer records than the page size or the current page has no records, or maximum page number is hit
        if (self._page_size and len(last_records) < self._page_size) or len(last_records) == 0:
            return None
        elif self._page >= self.PAGE_LIMIT:
            # reset page count as cursor parameter will be updated in the stream slicer
            self.reset()
            # get last_record from latest batch, pos. -1, because of ACS order of records
            last_record_updated_at = last_records[-1]["updated_at"]
            # updating slicer request parameters with last_record state
            return last_record_updated_at
        else:
            self._page += 1
            return self._page
