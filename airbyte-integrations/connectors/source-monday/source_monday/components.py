#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from datetime import datetime
from typing import Any, Iterable, List, Mapping, Optional, Union

import dpath.util
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream

RequestInput = Union[str, Mapping[str, str]]


def is_valid_format(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        return True
    except ValueError:
        return False


def get_max_date_string(str1, str2):
    if not is_valid_format(str1) or not is_valid_format(str2):
        raise ValueError("Invalid date format")

    dt1 = datetime.strptime(str1, "%Y-%m-%dT%H:%M:%SZ")
    dt2 = datetime.strptime(str2, "%Y-%m-%dT%H:%M:%SZ")
    max_dt = max(dt1, dt2)
    return max_dt.strftime("%Y-%m-%dT%H:%M:%SZ")


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
            if isinstance(current_state_value, str):
                cursor = get_max_date_string(current_state_value, last_record_value)
            else:
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
            self._cursor.update(
                **{self.cursor_field.eval(self.config): self._get_max_state_value(updated_cursor_value, current_cursor_value)}
            )
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
    items_per_request: int = field(default=100)
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
        self,
        current_state_value: Optional[Union[int, str]],
        last_record_value: Optional[Union[int, str]],
    ) -> Optional[Union[int, str]]:
        if current_state_value and last_record_value:
            if isinstance(current_state_value, str):
                cursor = get_max_date_string(current_state_value, last_record_value)
            else:
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
            max_value = self._get_max_state_value(current_cursor_value, updated_cursor_value)
            if parent:
                self._cursor.update(**{self.parent_stream_name: {self.parent_cursor_field: max_value}})
            else:
                self._cursor.update(**{self.cursor_field.eval(self.config): max_value})
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
                parent=True,
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
        if not stream_slice:
            sub_cursor_field = self.cursor_field.eval(self.config)
            print(f"{sub_cursor_field=}")
            date_str = last_record[sub_cursor_field]
            parent_cursor = int(datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").timestamp())
            slice = {self.parent_stream_name: {self.parent_cursor_field: parent_cursor}}
            self._update_parent_cursor(slice)

    def read_parent_stream(
        self, sync_mode: SyncMode, cursor_field: Optional[str], stream_state: Mapping[str, Any]
    ) -> Iterable[Mapping[str, Any]]:

        for parent_slice in self.parent_stream.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state):
            empty_parent_slice = True

            # update slice with parent state, to pass the initial parent state to the parent instance
            # stream_state is being replaced by empty object, since the parent stream is not directly initiated
            parent_prior_state = self._cursor.get("prior_state", {}).get(self.parent_stream_name, {}).get(self.parent_cursor_field)
            print(f"{parent_prior_state=} {self.parent_cursor_field=}")
            parent_slice.update({"prior_state": {self.parent_cursor_field: parent_prior_state}})
            # add check if state is empty ->
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
                        slice[self.cursor_field.eval(self.config)] = self._cursor.get(self.cursor_field.eval(self.config))
                        slice[self.parent_stream_name] = {
                            self.parent_cursor_field: self._cursor.get(self.parent_stream_name, {}).get(self.parent_cursor_field)
                        }
                        self._update_parent_cursor(slice, parent_record)

                        print(f"{slice=}")
                        # track and update the parent cursor
                        if self.items_per_request == len(slice[self.substream_slice_field]):
                            yield slice
                            slice[self.substream_slice_field] = list()
                if slice[self.substream_slice_field]:
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
