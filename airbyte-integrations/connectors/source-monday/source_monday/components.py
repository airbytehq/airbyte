#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from datetime import datetime
from typing import Any, Iterable, List, Mapping, Optional, Union

import dpath.util
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.incremental import Cursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream

RequestInput = Union[str, Mapping[str, str]]


def is_valid_format(date_string: str) -> bool:
    try:
        datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        return True
    except ValueError:
        return False


def compare_date_strings(str1: str, str2: str) -> bool:
    if not is_valid_format(str1) or not is_valid_format(str2):
        raise ValueError("Invalid date format")

    dt1 = datetime.strptime(str1, "%Y-%m-%dT%H:%M:%SZ")
    dt2 = datetime.strptime(str2, "%Y-%m-%dT%H:%M:%SZ")
    return dt1 > dt2


@dataclass
class IncrementalSingleSlice(Cursor):
    cursor_field: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._state = {}
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
        return self._state

    def _get_max_state_value(
        self,
        current_state_value: Optional[Union[int, str]],
        last_record_value: Optional[Union[int, str]],
    ) -> Optional[Union[int, str]]:
        if isinstance(last_record_value, str) and isinstance(current_state_value, str):
            return compare_date_strings(current_state_value, last_record_value)
        elif isinstance(last_record_value, int) and isinstance(current_state_value, int):
            return current_state_value > last_record_value
        elif last_record_value:
            return False
        else:
            return True

    def set_initial_state(self, stream_state: StreamState):
        cursor_value = stream_state.get(self.cursor_field.eval(self.config))
        if cursor_value:
            self._state[self.cursor_field.eval(self.config)] = cursor_value

    def close_slice(self, stream_slice: StreamSlice, most_recent_record: Optional[Record]) -> None:
        max_dt = self._state if self.is_greater_than_or_equal(self._state, most_recent_record) else most_recent_record

        if not max_dt:
            return
        self._state[self.cursor_field.eval(self.config)] = max_dt[self.cursor_field.eval(self.config)]

    def stream_slices(self) -> Iterable[Mapping[str, Any]]:
        yield {}

    def should_be_synced(self, record: Record) -> bool:
        """
        As of 2023-06-28, the expectation is that this method will only be used for semi-incremental and data feed and therefore the
        implementation is irrelevant for greenhouse
        """
        return True

    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        """
        Evaluating which record is greater in terms of cursor. This is used to avoid having to capture all the records to close a slice
        """
        first_cursor_value = first.get(self.cursor_field.eval(self.config)) if first else None
        second_cursor_value = second.get(self.cursor_field.eval(self.config)) if second else None
        if first_cursor_value and second_cursor_value:
            return self._get_max_state_value(first_cursor_value, second_cursor_value)
        elif first_cursor_value:
            return True
        else:
            return False


@dataclass
class IncrementalSubstreamSlicer(IncrementalSingleSlice):
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
    items_per_request: int = field(default=100)
    parent_complete_fetch: bool = field(default=False)

    def __post_init__(self, parameters: Mapping[str, Any]):
        super().__post_init__(parameters)
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

    def set_initial_state(self, stream_state: StreamState):
        cursor_value = stream_state.get(self.cursor_field.eval(self.config))
        if cursor_value:
            self._state[self.cursor_field.eval(self.config)] = cursor_value
        if self.parent_stream_name in stream_state and stream_state.get(self.parent_stream_name, {}).get(self.parent_cursor_field):
            self._state[self.parent_stream_name] = {
                self.parent_cursor_field: stream_state[self.parent_stream_name][self.parent_cursor_field]
            }

    def close_slice(self, stream_slice: StreamSlice, most_recent_record: Optional[Record]) -> None:
        max_dt = self._state if self.is_greater_than_or_equal(self._state, most_recent_record) else most_recent_record

        if not max_dt:
            return
        self._state[self.cursor_field.eval(self.config)] = max_dt[self.cursor_field.eval(self.config)]

        if self.parent_stream:
            if self.parent_cursor_field not in most_recent_record:
                date_str = most_recent_record[self.cursor_field.eval(self.config)]
                parent_cursor = int(datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").timestamp())
            else:
                parent_cursor = most_recent_record[self.parent_cursor_field]
            self._state[self.parent_stream_name] = {self.parent_cursor_field: parent_cursor}

    def read_parent_stream(
        self, sync_mode: SyncMode, cursor_field: Optional[str], stream_state: Mapping[str, Any]
    ) -> Iterable[Mapping[str, Any]]:
        self.parent_stream.state = stream_state
        for parent_slice in self.parent_stream.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state):
            empty_parent_slice = True

            # check if state is empty ->
            if not stream_state.get(self.parent_cursor_field):
                # yield empty slice for complete fetch of items stream
                yield from [
                    {},
                ]
            else:
                slice = {self.substream_slice_field: list()}
                all_ids = set()

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

                        if substream_slice not in all_ids:
                            all_ids.add(substream_slice)
                            slice[self.substream_slice_field].append(substream_slice)

                        if self.items_per_request == len(slice[self.substream_slice_field]):
                            yield slice
                            slice[self.substream_slice_field] = list()
                if slice[self.substream_slice_field]:
                    yield slice

            # If the parent slice contains no records,
            if empty_parent_slice:
                yield from []

    def stream_slices(self) -> Iterable[Mapping[str, Any]]:
        parent_state = (self._state or {}).get(self.parent_stream_name, {})

        slices_generator = self.read_parent_stream(self.parent_sync_mode, self.parent_cursor_field, parent_state)
        if self.parent_complete_fetch:
            yield from [slice for slice in slices_generator]
        else:
            yield from slices_generator
