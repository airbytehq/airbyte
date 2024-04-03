import datetime

from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, List, Mapping, Optional, Union
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.incremental.datetime_based_cursor import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.incremental.cursor import Cursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream

@dataclass
class AppointmentsDatetimeBasedCursor(DatetimeBasedCursor):
  def _select_best_end_datetime(self) -> datetime.datetime:
    now = datetime.datetime.now(tz=self._timezone)
    if not self._end_datetime:
        return now
    return self._end_datetime.get_datetime(self.config)

  def _calculate_cursor_datetime_from_state(self, stream_state: Mapping[str, Any]) -> datetime.datetime:
    if self._cursor_field.eval(self.config, stream_state=stream_state) in stream_state:
      return datetime.datetime.now(tz=self._timezone)
    return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)


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

    def close_slice(self, stream_slice: StreamSlice) -> None:
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

    def set_initial_state(self, stream_state: StreamState):
        super().set_initial_state(stream_state=stream_state)
        self._state = stream_state

    def stream_slices(self) -> Iterable[Mapping[str, Any]]:
        parent_state = self._state.get(self.parent_stream_name, {})
        slices_generator: Iterable[StreamSlice] = self.read_parent_stream(self.parent_sync_mode, self.parent_cursor_field, parent_state)
        yield from [slice for slice in slices_generator] if self.parent_complete_fetch else slices_generator

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
                substream_slice_value = parent_record.get(self.parent_field)
                if substream_slice_value:
                    yield StreamSlice(
                        partition={
                            self.substream_slice_field: substream_slice_value,
                        },
                        cursor_slice={},
                    )
            self._state[self.parent_stream_name] = self.parent_stream.retriever.state
