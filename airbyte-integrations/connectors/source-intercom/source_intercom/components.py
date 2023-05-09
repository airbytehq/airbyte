#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from dataclasses import InitVar, dataclass, field
from functools import lru_cache, wraps
from time import sleep
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import dpath.util
import requests
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator, NoAuth
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_input_provider import InterpolatedRequestInputProvider
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod, Requester
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream

RequestInput = Union[str, Mapping[str, str]]


@dataclass
class IncrementalSingleSlice(StreamSlicer):

    cursor_field: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    _cursor: dict = field(default_factory=dict)
    initial_state: dict = field(default_factory=dict)

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.cursor_field = InterpolatedString.create(self.cursor_field, parameters=parameters)

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.request_parameter, stream_slice)

    def get_request_headers(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.header, stream_slice)

    def get_request_body_data(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.body_data, stream_slice)

    def get_request_body_json(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.body_json, stream_slice)

    def _get_request_option(self, option_type: RequestOptionType, stream_slice: StreamSlice):
        return {}

    def get_stream_state(self) -> StreamState:
        return self._cursor if self._cursor else {}

    def _get_max_state_value(
        self,
        current_state_value: Optional[Union[int, str]],
        last_record_value: Optional[Union[int, str]],
    ) -> Optional[Union[int, str]]:
        if current_state_value and last_record_value:
            cursor = max(current_state_value, last_record_value)
        elif current_state_value:
            cursor = current_state_value
        else:
            cursor = last_record_value
        return cursor

    def _set_initial_state(self, stream_slice: StreamSlice):
        self.initial_state = stream_slice if not self.initial_state else self.initial_state

    def _update_cursor_with_prior_state(self):
        self._cursor["prior_state"] = {self.cursor_field.eval(self.config): self.initial_state.get(self.cursor_field.eval(self.config))}

    def _get_current_state(self, stream_slice: StreamSlice) -> Union[str, float, int]:
        return stream_slice.get(self.cursor_field.eval(self.config))

    def _get_last_record_value(self, last_record: Optional[Record] = None) -> Union[str, float, int]:
        return last_record.get(self.cursor_field.eval(self.config)) if last_record else None

    def _get_current_cursor_value(self) -> Union[str, float, int]:
        return self._cursor.get(self.cursor_field.eval(self.config)) if self._cursor else None

    def _update_current_cursor(
        self,
        current_cursor_value: Optional[Union[str, float, int]] = None,
        updated_cursor_value: Optional[Union[str, float, int]] = None,
    ):
        if current_cursor_value and updated_cursor_value:
            self._cursor.update(**{self.cursor_field.eval(self.config): max(updated_cursor_value, current_cursor_value)})
        elif updated_cursor_value:
            self._cursor.update(**{self.cursor_field.eval(self.config): updated_cursor_value})

    def _update_stream_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        self._update_current_cursor(
            self._get_current_cursor_value(),
            self._get_max_state_value(
                self._get_current_state(stream_slice),
                self._get_last_record_value(last_record),
            ),
        )

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        # freeze initial state
        self._set_initial_state(stream_slice)
        # update the state of the child stream cursor_field value from previous sync,
        # and freeze it to have an ability to compare the record vs state
        self._update_cursor_with_prior_state()
        self._update_stream_cursor(stream_slice, last_record)

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        yield {}


@dataclass
class IncrementalSubstreamSlicer(StreamSlicer):
    """
    Like SubstreamSlicer, but works incrementaly with both parent and substream.

    Input Arguments:

    :: cursor_field: srt - substream cursor_field value
    :: parent_complete_fetch: bool - If `True`, all slices is fetched into a list first, then yield.
        If `False`, substream emits records on each parernt slice yield.
    :: parent_stream_configs: ParentStreamConfig - Describes how to create a stream slice from a parent stream.

    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    cursor_field: Union[InterpolatedString, str]
    parent_stream_configs: List[ParentStreamConfig]
    parent_complete_fetch: bool = field(default=False)
    _cursor: dict = field(default_factory=dict)
    initial_state: dict = field(default_factory=dict)

    def __post_init__(self, parameters: Mapping[str, Any]):
        if not self.parent_stream_configs:
            raise ValueError("IncrementalSubstreamSlicer needs at least 1 parent stream")
        self.cursor_field = InterpolatedString.create(self.cursor_field, parameters=parameters)
        # parent stream parts
        self.parent_config: ParentStreamConfig = self.parent_stream_configs[0]
        self.parent_stream: Stream = self.parent_config.stream
        self.parent_stream_name: str = self.parent_stream.name
        self.parent_cursor_field: str = self.parent_stream.cursor_field
        self.parent_sync_mode: SyncMode = SyncMode.incremental if self.parent_stream.supports_incremental is True else SyncMode.full_refresh
        self.substream_slice_field: str = self.parent_stream_configs[0].partition_field.eval(self.config)
        self.parent_field: str = self.parent_stream_configs[0].parent_key.eval(self.config)

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.request_parameter, stream_slice)

    def get_request_headers(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.header, stream_slice)

    def get_request_body_data(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.body_data, stream_slice)

    def get_request_body_json(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.body_json, stream_slice)

    def _get_request_option(self, option_type: RequestOptionType, stream_slice: StreamSlice):
        return {}

    def _get_max_state_value(
        self, current_state_value: Optional[Union[int, str]], last_record_value: Optional[Union[int, str]]
    ) -> Optional[Union[int, str]]:
        if current_state_value and last_record_value:
            cursor = max(current_state_value, last_record_value)
        elif current_state_value:
            cursor = current_state_value
        else:
            cursor = last_record_value
        return cursor

    def _set_initial_state(self, stream_slice: StreamSlice):
        self.initial_state = stream_slice if not self.initial_state else self.initial_state

    def _get_last_record_value(self, last_record: Optional[Record] = None, parent: Optional[bool] = False) -> Union[str, float, int]:
        if parent:
            return last_record.get(self.parent_cursor_field) if last_record else None
        else:
            return last_record.get(self.cursor_field.eval(self.config)) if last_record else None

    def _get_current_cursor_value(self, parent: Optional[bool] = False) -> Union[str, float, int]:
        if parent:
            return self._cursor.get(self.parent_stream_name, {}).get(self.parent_cursor_field) if self._cursor else None
        else:
            return self._cursor.get(self.cursor_field.eval(self.config)) if self._cursor else None

    def _get_current_state(self, stream_slice: StreamSlice, parent: Optional[bool] = False) -> Union[str, float, int]:
        if parent:
            return stream_slice.get(self.parent_stream_name, {}).get(self.parent_cursor_field)
        else:
            return stream_slice.get(self.cursor_field.eval(self.config))

    def _update_current_cursor(
        self,
        current_cursor_value: Optional[Union[str, float, int]] = None,
        updated_cursor_value: Optional[Union[str, float, int]] = None,
        parent: Optional[bool] = False,
    ):
        if current_cursor_value and updated_cursor_value:
            if parent:
                self._cursor.update(
                    **{self.parent_stream_name: {self.parent_cursor_field: max(updated_cursor_value, current_cursor_value)}}
                )
            else:
                self._cursor.update(**{self.cursor_field.eval(self.config): max(updated_cursor_value, current_cursor_value)})
        elif updated_cursor_value:
            if parent:
                self._cursor.update(**{self.parent_stream_name: {self.parent_cursor_field: updated_cursor_value}})
            else:
                self._cursor.update(**{self.cursor_field.eval(self.config): updated_cursor_value})

    def _update_substream_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        self._update_current_cursor(
            self._get_current_cursor_value(),
            self._get_max_state_value(
                self._get_current_state(stream_slice),
                self._get_last_record_value(last_record),
            ),
        )

    def _update_parent_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        if self.parent_cursor_field:
            self._update_current_cursor(
                self._get_current_cursor_value(parent=True),
                self._get_max_state_value(
                    self._get_current_state(stream_slice, parent=True),
                    self._get_last_record_value(last_record, parent=True),
                ),
            )

    def _update_cursor_with_prior_state(self):
        self._cursor["prior_state"] = {
            self.cursor_field.eval(self.config): self.initial_state.get(self.cursor_field.eval(self.config)),
            self.parent_stream_name: {
                self.parent_cursor_field: self.initial_state.get(self.parent_stream_name, {}).get(self.parent_cursor_field)
            },
        }

    def get_stream_state(self) -> StreamState:
        return self._cursor if self._cursor else {}

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        # freeze initial state
        self._set_initial_state(stream_slice)
        # update the state of the child stream cursor_field value from previous sync,
        # and freeze it to have an ability to compare the record vs state
        self._update_cursor_with_prior_state()
        # we focus on updating the substream's cursor in this method,
        # the parent's cursor is updated while reading parent stream
        self._update_substream_cursor(stream_slice, last_record)

    def read_parent_stream(
        self, sync_mode: SyncMode, cursor_field: Optional[str], stream_state: Mapping[str, Any]
    ) -> Iterable[Mapping[str, Any]]:

        for parent_slice in self.parent_stream.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state):
            empty_parent_slice = True

            # update slice with parent state, to pass the initial parent state to the parent instance
            # stream_state is being replaced by empty object, since the parent stream is not directly initiated
            parent_prior_state = self._cursor.get("prior_state", {}).get(self.parent_stream_name, {}).get(self.parent_cursor_field)
            parent_slice.update({"prior_state": {self.parent_cursor_field: parent_prior_state}})

            for parent_record in self.parent_stream.read_records(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=parent_slice, stream_state=stream_state
            ):
                # Skip non-records (eg AirbyteLogMessage)
                if isinstance(parent_record, AirbyteMessage):
                    if parent_record.type == Type.RECORD:
                        parent_record = parent_record.record.data

                try:
                    substream_slice = dpath.util.get(parent_record, self.parent_field)
                except KeyError:
                    pass
                else:
                    empty_parent_slice = False
                    slice = {
                        self.substream_slice_field: substream_slice,
                        self.cursor_field.eval(self.config): self._cursor.get(self.cursor_field.eval(self.config)),
                        self.parent_stream_name: {
                            self.parent_cursor_field: self._cursor.get(self.parent_stream_name, {}).get(self.parent_cursor_field)
                        },
                    }
                    # track and update the parent cursor
                    self._update_parent_cursor(slice, parent_record)
                    yield slice

            # If the parent slice contains no records,
            if empty_parent_slice:
                yield from []

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        stream_state = self.initial_state or {}
        parent_state = stream_state.get(self.parent_stream_name, {})
        parent_state.update(**{"prior_state": self._cursor.get("prior_state", {}).get(self.parent_stream_name, {})})
        slices_generator = self.read_parent_stream(self.parent_sync_mode, self.parent_cursor_field, parent_state)
        if self.parent_complete_fetch:
            yield from [slice for slice in slices_generator]
        else:
            yield from slices_generator


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


@dataclass
class HttpRequesterWithRateLimiter(Requester):
    """
    The difference between the built-in `HttpRequester` and this one is the custom decorator,
    applied on top of `interpret_response_status` to preserve the api calls for a defined amount of time,
    calculated using the rate limit headers and not use the custom backoff strategy,
    since we deal with Response.status_code == 200,
    the default requester's logic doesn't allow to handle the status of 200 with `should_retry()`.

    Attributes:
        name (str): Name of the stream. Only used for request/response caching
        url_base (Union[InterpolatedString, str]): Base url to send requests to
        path (Union[InterpolatedString, str]): Path to send requests to
        http_method (Union[str, HttpMethod]): HTTP method to use when sending requests
        request_options_provider (Optional[InterpolatedRequestOptionsProvider]): request option provider defining the options to set on outgoing requests
        authenticator (DeclarativeAuthenticator): Authenticator defining how to authenticate to the source
        error_handler (Optional[ErrorHandler]): Error handler defining how to detect and handle errors
        config (Config): The user-provided configuration as specified by the source's spec
    """

    name: str
    url_base: Union[InterpolatedString, str]
    path: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    http_method: Union[str, HttpMethod] = HttpMethod.GET
    request_parameters: Optional[RequestInput] = None
    request_headers: Optional[RequestInput] = None
    request_body_data: Optional[RequestInput] = None
    request_body_json: Optional[RequestInput] = None
    authenticator: DeclarativeAuthenticator = None
    error_handler: Optional[ErrorHandler] = None

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.url_base = InterpolatedString.create(self.url_base, parameters=parameters)
        self.path = InterpolatedString.create(self.path, parameters=parameters)

        self.authenticator = self.authenticator or NoAuth(parameters=parameters)
        if type(self.http_method) == str:
            self.http_method = HttpMethod[self.http_method]
        self._method = self.http_method
        self.error_handler = self.error_handler or DefaultErrorHandler(parameters=parameters, config=self.config)
        self._parameters = parameters

        self.request_parameters = self.request_parameters if self.request_parameters else {}
        self.request_headers = self.request_headers if self.request_headers else {}
        self.request_body_data = self.request_body_data if self.request_body_data else {}
        self.request_body_json = self.request_body_json if self.request_body_json else {}

        if self.request_body_json and self.request_body_data:
            raise ValueError("RequestOptionsProvider should only contain either 'request_body_data' or 'request_body_json' not both")

        self._parameter_interpolator = InterpolatedRequestInputProvider(
            config=self.config, request_inputs=self.request_parameters, parameters=parameters
        )
        self._headers_interpolator = InterpolatedRequestInputProvider(
            config=self.config, request_inputs=self.request_headers, parameters=parameters
        )
        self._body_data_interpolator = InterpolatedRequestInputProvider(
            config=self.config, request_inputs=self.request_body_data, parameters=parameters
        )
        self._body_json_interpolator = InterpolatedRequestInputProvider(
            config=self.config, request_inputs=self.request_body_json, parameters=parameters
        )

    @property
    def cache_filename(self) -> str:
        return f"{self.name}.yml"

    @property
    def use_cache(self) -> bool:
        return False

    def __hash__(self):
        return hash(tuple(self.__dict__))

    def get_authenticator(self):
        return self.authenticator

    def get_url_base(self):
        return os.path.join(self.url_base.eval(self.config), "")

    def get_path(
        self, *, stream_state: Optional[StreamState], stream_slice: Optional[StreamSlice], next_page_token: Optional[Mapping[str, Any]]
    ) -> str:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        path = self.path.eval(self.config, **kwargs)
        return path.strip("/")

    def get_method(self):
        return self._method

    # The RateLimiter is applied to balance the api requests.
    @lru_cache(maxsize=10)
    @IntercomRateLimiter.balance_rate_limit()
    def interpret_response_status(self, response: requests.Response) -> ResponseStatus:
        # Check for response.headers to define the backoff time before the next api call
        return self.error_handler.interpret_response(response)

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

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Union[Mapping, str]]:
        return self._body_data_interpolator.eval_request_inputs(stream_state, stream_slice, next_page_token)

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        return self._body_json_interpolator.eval_request_inputs(stream_state, stream_slice, next_page_token)

    def request_kwargs(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}
