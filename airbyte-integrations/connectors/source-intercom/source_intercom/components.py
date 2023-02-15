#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, List, Mapping, Optional, Union

import dpath.util
import requests
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.header_helper import get_numeric_value_from_header
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategy import BackoffStrategy
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.substream_slicer import ParentStreamConfig
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class IncrementalSingleSlice(StreamSlicer, JsonSchemaMixin):

    cursor_field: Union[InterpolatedString, str]
    config: Config
    options: InitVar[Mapping[str, Any]]
    _cursor: dict = field(default_factory=dict)
    initial_state: dict = field(default_factory=dict)

    def __post_init__(self, options: Mapping[str, Any]):
        self.cursor_field = InterpolatedString.create(self.cursor_field, options=options)

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
        self, current_state_value: Optional[Union[int, str]], last_record_value: Optional[Union[int, str]]
    ) -> Optional[Union[int, str]]:
        if current_state_value and last_record_value:
            cursor = max(current_state_value, last_record_value)
        elif current_state_value:
            cursor = current_state_value
        else:
            cursor = last_record_value
        return cursor

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        self.initial_state = stream_slice if not self.initial_state else self.initial_state
        self._cursor["prior_state"] = {self.cursor_field.eval(self.config): self.initial_state.get(self.cursor_field.eval(self.config))}

        stream_state_value = stream_slice.get(self.cursor_field.eval(self.config))
        last_record_value = last_record.get(self.cursor_field.eval(self.config)) if last_record else None
        current_state = self._cursor.get(self.cursor_field.eval(self.config)) if self._cursor else None
        stream_cursor = self._get_max_state_value(stream_state_value, last_record_value)
        if current_state and stream_cursor:
            self._cursor.update(**{self.cursor_field.eval(self.config): max(stream_cursor, current_state)})
        elif stream_cursor:
            self._cursor.update(**{self.cursor_field.eval(self.config): stream_cursor})

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        yield {}


@dataclass
class IncrementalSubstreamSlicer(StreamSlicer, JsonSchemaMixin):
    """
    Like SubstreamSlicer, but works incrementaly with both parent and substream.

    Input Arguments:

    :: cursor_field: srt - substream cursor_field value
    :: parent_complete_fetch: bool - If `True`, all slices is fetched into a list first, then yield.
        If `False`, substream emits records on each parernt slice yield.
    :: parent_stream_configs: ParentStreamConfig - Describes how to create a stream slice from a parent stream.

    """

    config: Config
    options: InitVar[Mapping[str, Any]]
    cursor_field: Union[InterpolatedString, str]
    parent_stream_configs: List[ParentStreamConfig]
    parent_complete_fetch: bool = field(default=False)
    _cursor: dict = field(default_factory=dict)
    initial_state: dict = field(default_factory=dict)

    def __post_init__(self, options: Mapping[str, Any]):
        if not self.parent_stream_configs:
            raise ValueError("IncrementalSubstreamSlicer needs at least 1 parent stream")
        self.cursor_field = InterpolatedString.create(self.cursor_field, options=options)
        # parent stream parts
        self.parent_config: ParentStreamConfig = self.parent_stream_configs[0]
        self.parent_stream: Stream = self.parent_config.stream
        self.parent_stream_name: str = self.parent_stream.name
        self.parent_cursor_field: str = self.parent_stream.cursor_field
        self.parent_sync_mode: SyncMode = SyncMode.incremental if self.parent_stream.supports_incremental is True else SyncMode.full_refresh
        self.substream_slice_field: str = self.parent_stream_configs[0].stream_slice_field.eval(self.config)
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

    def get_stream_state(self) -> StreamState:
        return self._cursor if self._cursor else {}

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

    def _update_substream_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        substream_state_value = stream_slice.get(self.cursor_field.eval(self.config))
        last_record_value = last_record.get(self.cursor_field.eval(self.config)) if last_record else None
        current_state = self._cursor.get(self.cursor_field.eval(self.config)) if self._cursor else None
        substream_cursor = self._get_max_state_value(substream_state_value, last_record_value)
        if current_state and substream_cursor:
            self._cursor.update(**{self.cursor_field.eval(self.config): max(substream_cursor, current_state)})
        elif substream_cursor:
            self._cursor.update(**{self.cursor_field.eval(self.config): substream_cursor})

    def _update_parent_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        if self.parent_cursor_field:
            parent_state_value = stream_slice.get(self.parent_stream_name, {}).get(self.parent_cursor_field)
            last_record_value = last_record.get(self.parent_cursor_field) if last_record else None
            current_state = self._cursor.get(self.parent_stream_name, {}).get(self.parent_cursor_field) if self._cursor else None
            parent_cursor = self._get_max_state_value(parent_state_value, last_record_value)
            if current_state and parent_cursor:
                self._cursor.update(**{self.parent_stream_name: {self.parent_cursor_field: max(parent_cursor, current_state)}})
            elif parent_cursor:
                self._cursor.update(**{self.parent_stream_name: {self.parent_cursor_field: parent_cursor}})

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        # freeze initial state
        self.initial_state = stream_slice if not self.initial_state else self.initial_state
        # update the state of the child stream cursor_field value from previous sync,
        # and freeze it to have an ability to compare the record vs state
        self._cursor["prior_state"] = {
            self.cursor_field.eval(self.config): self.initial_state.get(self.cursor_field.eval(self.config)),
            self.parent_stream_name: {
                self.parent_cursor_field: self.initial_state.get(self.parent_stream_name, {}).get(self.parent_cursor_field)
            },
        }
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
class LoadBasedWaitTimeFromHeaderBackoffStrategy(BackoffStrategy, JsonSchemaMixin):
    """
    To avoid reaching Intercom API Rate Limits, use the 'X-RateLimit-Limit','X-RateLimit-Remaining' header values,
    to determine the current rate limits and load and handle wait_time based on load %.
    Recomended wait_time between each request is 1 sec, we would handle this dynamicaly.

    :: current_rate_header - responce header item, contains information with max rate_limits available (max)
    :: regex_current_rate_header - same as `current_rate_header`, but uses `RegExp` to fetch the header value
    :: total_rate_header - responce header item, contains information with how many requests are still available (current)
    :: regex_total_rate_header - same as `total_rate_header`, but uses `RegExp` to fetch the header value
    :: threshold - is the % cutoff for the rate_limits % load, if this cutoff is crossed,
        the connector waits `x` amount of time, default value = 0.1 (10% left from max capacity)

    Header example:
    {
        X-RateLimit-Limit: 100
        X-RateLimit-Remaining: 51
        X-RateLimit-Reset: 1487332510
    },
        where: 51 - requests remains and goes down, 100 - max requests capacity.

    More information: https://developers.intercom.com/intercom-api-reference/reference/rate-limiting
    """

    config: Config
    options: InitVar[Mapping[str, Any]]
    current_rate_header: Union[InterpolatedString, str]
    total_rate_header: Union[InterpolatedString, str]
    threshold: float = field(default=float)
    wait_on_load: Mapping[str, float] = field(default_factory=dict)
    regex_current_rate_header: Optional[str] = None
    regex_total_rate_header: Optional[str] = None

    def __post_init__(self, options: Mapping[str, Any]):
        self.current_rate_header = InterpolatedString.create(self.current_rate_header, options=options)
        self.total_rate_header = InterpolatedString.create(self.total_rate_header, options=options)
        self.regex_current_rate_header = re.compile(self.regex_current_rate_header) if self.regex_current_rate_header else None
        self.regex_total_rate_header = re.compile(self.regex_total_rate_header) if self.regex_total_rate_header else None

    def backoff(self, response: requests.Response, attempt_count: int) -> Optional[float]:
        current_rate_header: str = self.current_rate_header.eval(config=self.config)
        total_rate_header: str = self.total_rate_header.eval(config=self.config)
        current_rate_header_value: float = get_numeric_value_from_header(response, current_rate_header, self.regex_current_rate_header)
        total_rate_header_value: float = get_numeric_value_from_header(response, total_rate_header, self.regex_total_rate_header)

        # define current load and mid_load from rate_limits
        if current_rate_header_value and total_rate_header_value:
            mid_load: float = (total_rate_header_value / 2) / total_rate_header_value
            load: float = current_rate_header_value / total_rate_header_value
        else:
            # to guarantee mid_load value is 1 sec if headers are not available
            mid_load: float = self.threshold * (1 / self.threshold)
            load = None
        # define wait_time based on load conditions
        if not load:
            wait_time = self.wait_on_load.get("unknown")
        elif load <= self.threshold:
            wait_time = self.wait_on_load.get("max")
        elif load <= mid_load:
            wait_time = self.wait_on_load.get("avg")
        elif load > mid_load:
            wait_time = self.wait_on_load.get("min")
        return wait_time
