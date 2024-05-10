#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from functools import wraps
from time import sleep
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.incremental.cursor import Cursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_nested_request_input_provider import (
    InterpolatedNestedRequestInputProvider,
)
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_input_provider import InterpolatedRequestInputProvider
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream

RequestInput = Union[str, Mapping[str, str]]


@dataclass
class IncrementalSingleSliceCursor(Cursor):
    cursor_field: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._state = {}
        self._cursor = None
        self.cursor_field = InterpolatedString.create(self.cursor_field, parameters=parameters)

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Current implementation does not provide any options to update request params.
        # Returns empty dict
        return self._get_request_option(RequestOptionType.request_parameter, stream_slice)

    def get_request_headers(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Current implementation does not provide any options to update request headers.
        # Returns empty dict
        return self._get_request_option(RequestOptionType.header, stream_slice)

    def get_request_body_data(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Current implementation does not provide any options to update body data.
        # Returns empty dict
        return self._get_request_option(RequestOptionType.body_data, stream_slice)

    def get_request_body_json(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        # Current implementation does not provide any options to update body json.
        # Returns empty dict
        return self._get_request_option(RequestOptionType.body_json, stream_slice)

    def _get_request_option(self, option_type: RequestOptionType, stream_slice: StreamSlice):
        return {}

    def get_stream_state(self) -> StreamState:
        return self._state

    def set_initial_state(self, stream_state: StreamState):
        cursor_field = self.cursor_field.eval(self.config)
        cursor_value = stream_state.get(cursor_field)
        if cursor_value:
            self._state[cursor_field] = cursor_value
            self._state["prior_state"] = self._state.copy()
            self._cursor = cursor_value

    def observe(self, stream_slice: StreamSlice, record: Record) -> None:
        """
        Register a record with the cursor; the cursor instance can then use it to manage the state of the in-progress stream read.

        :param stream_slice: The current slice, which may or may not contain the most recently observed record
        :param record: the most recently-read record, which the cursor can use to update the stream state. Outwardly-visible changes to the
          stream state may need to be deferred depending on whether the source reliably orders records by the cursor field.
        """
        record_cursor_value = record.get(self.cursor_field.eval(self.config))
        if not record_cursor_value:
            return

        if self.is_greater_than_or_equal(record, self._state):
            self._cursor = record_cursor_value

    def close_slice(self, stream_slice: StreamSlice, *args: Any) -> None:
        cursor_field = self.cursor_field.eval(self.config)
        self._state[cursor_field] = self._cursor

    def stream_slices(self) -> Iterable[Mapping[str, Any]]:
        yield StreamSlice(partition={}, cursor_slice={})

    def should_be_synced(self, record: Record) -> bool:
        """
        Evaluating if a record should be synced allows for filtering and stop condition on pagination
        """
        record_cursor_value = record.get(self.cursor_field.eval(self.config))
        return bool(record_cursor_value)

    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        """
        Evaluating which record is greater in terms of cursor. This is used to avoid having to capture all the records to close a slice
        """
        cursor_field = self.cursor_field.eval(self.config)
        first_cursor_value = first.get(cursor_field) if first else None
        second_cursor_value = second.get(cursor_field) if second else None
        if first_cursor_value and second_cursor_value:
            return first_cursor_value > second_cursor_value
        elif first_cursor_value:
            return True
        else:
            return False


@dataclass
class IncrementalSubstreamSlicerCursor(IncrementalSingleSliceCursor):
    parent_stream_configs: List[ParentStreamConfig]
    parent_complete_fetch: bool = field(default=False)

    def __post_init__(self, parameters: Mapping[str, Any]):
        super().__post_init__(parameters)

        if not self.parent_stream_configs:
            raise ValueError("IncrementalSubstreamSlicer needs at least 1 parent stream")

        # parent stream parts
        self.parent_config: ParentStreamConfig = self.parent_stream_configs[0]
        self.parent_stream: Stream = self.parent_config.stream
        self.parent_stream_name: str = self.parent_stream.name
        self.parent_cursor_field: str = self.parent_stream.cursor_field
        self.parent_sync_mode: SyncMode = SyncMode.incremental if self.parent_stream.supports_incremental is True else SyncMode.full_refresh
        self.substream_slice_field: str = self.parent_stream_configs[0].partition_field.eval(self.config)
        self.parent_field: str = self.parent_stream_configs[0].parent_key.eval(self.config)
        self._parent_cursor: Optional[str] = None

    def set_initial_state(self, stream_state: StreamState):
        super().set_initial_state(stream_state=stream_state)
        if self.parent_stream_name in stream_state and stream_state.get(self.parent_stream_name, {}).get(self.parent_cursor_field):
            parent_stream_state = {
                self.parent_cursor_field: stream_state[self.parent_stream_name][self.parent_cursor_field],
            }
            self._state[self.parent_stream_name] = parent_stream_state
            if "prior_state" in self._state:
                self._state["prior_state"][self.parent_stream_name] = parent_stream_state

    def observe(self, stream_slice: StreamSlice, record: Record) -> None:
        """
        Extended the default method to be able to track the parent STATE.
        """

        # save parent cursor value (STATE) from slice
        parent_cursor = stream_slice.get(self.parent_stream_name)
        if parent_cursor:
            self._parent_cursor = parent_cursor.get(self.parent_cursor_field)

        # observe the substream
        super().observe(stream_slice, record)

    def close_slice(self, stream_slice: StreamSlice, *args: Any) -> None:
        super().close_slice(stream_slice, *args)

    def stream_slices(self) -> Iterable[Mapping[str, Any]]:
        parent_state = (self._state or {}).get(self.parent_stream_name, {})
        slices_generator: Iterable[StreamSlice] = self.read_parent_stream(self.parent_sync_mode, self.parent_cursor_field, parent_state)
        yield from [slice for slice in slices_generator] if self.parent_complete_fetch else slices_generator

    def track_parent_cursor(self, parent_record: dict) -> None:
        """
        Tracks the Parent Stream Cursor, using `parent_cursor_field`.
        """
        self._parent_cursor = parent_record.get(self.parent_cursor_field)
        if self._parent_cursor:
            self._state[self.parent_stream_name] = {self.parent_cursor_field: self._parent_cursor}

    def read_parent_stream(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[str],
        stream_state: Mapping[str, Any],
    ) -> Iterable[Mapping[str, Any]]:

        self.parent_stream.state = stream_state

        parent_stream_slices_gen = self.parent_stream.stream_slices(
            sync_mode=sync_mode,
            cursor_field=cursor_field,
            stream_state=stream_state,
        )

        for parent_slice in parent_stream_slices_gen:
            parent_records_gen = self.parent_stream.read_records(
                sync_mode=sync_mode,
                cursor_field=cursor_field,
                stream_slice=parent_slice,
                stream_state=stream_state,
            )

            for parent_record in parent_records_gen:
                # update parent cursor
                self.track_parent_cursor(parent_record)
                substream_slice_value = parent_record.get(self.parent_field)
                if substream_slice_value:
                    cursor_field = self.cursor_field.eval(self.config)
                    substream_cursor_value = self._state.get(cursor_field)
                    parent_cursor_value = self._state.get(self.parent_stream_name, {}).get(self.parent_cursor_field)
                    yield StreamSlice(
                        partition={
                            self.substream_slice_field: substream_slice_value,
                        },
                        cursor_slice={
                            cursor_field: substream_cursor_value,
                            self.parent_stream_name: {
                                self.parent_cursor_field: parent_cursor_value,
                            },
                        },
                    )


@dataclass
class IntercomRateLimiter:
    """
    Define timings for RateLimits. Adjust timings if needed.
    :: on_unknown_load = 1.0 sec - Intercom recommended time to hold between each API call.
    :: on_low_load = 0.01 sec (10 miliseconds) - ideal ratio between hold time and api call, also the standard hold time between each API call.
    :: on_mid_load = 1.5 sec - great timing to retrieve another 15% of request capacity while having mid_load.
    :: on_high_load = 8.0 sec - ideally we should wait 5.0 sec while having high_load, but we hold 8 sec to retrieve up to 80% of request capacity.
    """

    threshold: float = 0.1
    on_unknown_load: float = 1.0
    on_low_load: float = 0.01
    on_mid_load: float = 1.5
    on_high_load: float = 8.0  # max time

    @staticmethod
    def backoff_time(backoff_time: float):
        return sleep(backoff_time)

    @staticmethod
    def _define_values_from_headers(
        current_rate_header_value: Optional[float],
        total_rate_header_value: Optional[float],
        threshold: float = threshold,
    ) -> tuple[float, Union[float, str]]:
        # define current load and cutoff from rate_limits
        if current_rate_header_value and total_rate_header_value:
            cutoff: float = (total_rate_header_value / 2) / total_rate_header_value
            load: float = current_rate_header_value / total_rate_header_value
        else:
            # to guarantee cutoff value to be exactly 1 sec, based on threshold, if headers are not available
            cutoff: float = threshold * (1 / threshold)
            load = None
        return cutoff, load

    @staticmethod
    def _convert_load_to_backoff_time(
        cutoff: float,
        load: Optional[float] = None,
        threshold: float = threshold,
    ) -> float:
        # define backoff_time based on load conditions
        if not load:
            backoff_time = IntercomRateLimiter.on_unknown_load
        elif load <= threshold:
            backoff_time = IntercomRateLimiter.on_high_load
        elif load <= cutoff:
            backoff_time = IntercomRateLimiter.on_mid_load
        elif load > cutoff:
            backoff_time = IntercomRateLimiter.on_low_load
        return backoff_time

    @staticmethod
    def get_backoff_time(
        *args,
        threshold: float = threshold,
        rate_limit_header: str = "X-RateLimit-Limit",
        rate_limit_remain_header: str = "X-RateLimit-Remaining",
    ):
        """
        To avoid reaching Intercom API Rate Limits, use the 'X-RateLimit-Limit','X-RateLimit-Remaining' header values,
        to determine the current rate limits and load and handle backoff_time based on load %.
        Recomended backoff_time between each request is 1 sec, we would handle this dynamicaly.
        :: threshold - is the % cutoff for the rate_limits % load, if this cutoff is crossed,
                        the connector waits `sleep_on_high_load` amount of time, default value = 0.1 (10% left from max capacity)
        :: backoff_time - time between each request = 200 miliseconds
        :: rate_limit_header - responce header item, contains information with max rate_limits available (max)
        :: rate_limit_remain_header - responce header item, contains information with how many requests are still available (current)
        Header example:
        {
            X-RateLimit-Limit: 100
            X-RateLimit-Remaining: 51
            X-RateLimit-Reset: 1487332510
        },
            where: 51 - requests remains and goes down, 100 - max requests capacity.
        More information: https://developers.intercom.com/intercom-api-reference/reference/rate-limiting
        """

        # find the requests.Response inside args list
        for arg in args:
            if isinstance(arg, requests.models.Response):
                headers = arg.headers or {}

        # Get the rate_limits from response
        total_rate = int(headers.get(rate_limit_header, 0)) if headers else None
        current_rate = int(headers.get(rate_limit_remain_header, 0)) if headers else None
        cutoff, load = IntercomRateLimiter._define_values_from_headers(
            current_rate_header_value=current_rate,
            total_rate_header_value=total_rate,
            threshold=threshold,
        )

        backoff_time = IntercomRateLimiter._convert_load_to_backoff_time(cutoff=cutoff, load=load, threshold=threshold)
        return backoff_time

    @staticmethod
    def balance_rate_limit(
        threshold: float = threshold,
        rate_limit_header: str = "X-RateLimit-Limit",
        rate_limit_remain_header: str = "X-RateLimit-Remaining",
    ):
        """
        The decorator function.
        Adjust `threshold`,`rate_limit_header`,`rate_limit_remain_header` if needed.
        """

        def decorator(func):
            @wraps(func)
            def wrapper_balance_rate_limit(*args, **kwargs):
                IntercomRateLimiter.backoff_time(
                    IntercomRateLimiter.get_backoff_time(
                        *args, threshold=threshold, rate_limit_header=rate_limit_header, rate_limit_remain_header=rate_limit_remain_header
                    )
                )
                return func(*args, **kwargs)

            return wrapper_balance_rate_limit

        return decorator


@dataclass(eq=False)
class HttpRequesterWithRateLimiter(HttpRequester):
    """
    The difference between the built-in `HttpRequester` and this one is the custom decorator,
    applied on top of `interpret_response_status` to preserve the api calls for a defined amount of time,
    calculated using the rate limit headers and not use the custom backoff strategy,
    since we deal with Response.status_code == 200,
    the default requester's logic doesn't allow to handle the status of 200 with `should_retry()`.
    """

    request_body_json: Optional[RequestInput] = None
    request_headers: Optional[RequestInput] = None
    request_parameters: Optional[RequestInput] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)

        self.request_parameters = self.request_parameters if self.request_parameters else {}
        self.request_headers = self.request_headers if self.request_headers else {}
        self.request_body_json = self.request_body_json if self.request_body_json else {}

        self._parameter_interpolator = InterpolatedRequestInputProvider(
            config=self.config, request_inputs=self.request_parameters, parameters=parameters
        )
        self._headers_interpolator = InterpolatedRequestInputProvider(
            config=self.config, request_inputs=self.request_headers, parameters=parameters
        )
        self._body_json_interpolator = InterpolatedNestedRequestInputProvider(
            config=self.config, request_inputs=self.request_body_json, parameters=parameters
        )

    # The RateLimiter is applied to balance the api requests.
    @IntercomRateLimiter.balance_rate_limit()
    def interpret_response_status(self, response: requests.Response) -> ResponseStatus:
        # Check for response.headers to define the backoff time before the next api call
        return super().interpret_response_status(response)

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        interpolated_value = self._parameter_interpolator.eval_request_inputs(stream_state, stream_slice, next_page_token)
        if isinstance(interpolated_value, dict):
            return interpolated_value
        return {}

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._headers_interpolator.eval_request_inputs(stream_state, stream_slice, next_page_token)

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        return self._body_json_interpolator.eval_request_inputs(stream_state, stream_slice, next_page_token)
