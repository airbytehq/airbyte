#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime
from dataclasses import InitVar, dataclass
from typing import Any, Iterable, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState
from sources.declarative.incremental import DatetimeBasedCursor


@dataclass
class RecordFilter:
    """
    Filter applied on a list of Records

    config (Config): The user-provided configuration as specified by the source's spec
    condition (str): The string representing the predicate to filter a record. Records will be removed if evaluated to False
    """

    parameters: InitVar[Mapping[str, Any]]
    config: Config
    condition: str = ""

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._filter_interpolator = InterpolatedBoolean(condition=self.condition, parameters=parameters)

    def filter_records(
        self,
        records: Iterable[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        for record in records:
            if self._filter_interpolator.eval(self.config, record=record, **kwargs):
                yield record


class ClientSideIncrementalRecordFilterDecorator:
    """
    Filter applied on a list of Records to exclude ones that are older than stream_state/start_date
    config (Config): The user-provided configuration as specified by the source's spec
    """

    def __init__(self, date_time_based_cursor: DatetimeBasedCursor, record_filter: Optional[RecordFilter], partition_id: str = ""):
        self._date_time_based_cursor = date_time_based_cursor
        self._delegate = record_filter
        self._partition_id = partition_id

    @property
    def _cursor_field(self) -> Union[str, Any]:
        return self._date_time_based_cursor._cursor_field.eval(self._date_time_based_cursor.config)

    @property
    def _start_date_from_config(self) -> Union[datetime.datetime, Any]:
        return self._date_time_based_cursor._start_datetime.get_datetime(self._date_time_based_cursor.config)

    def filter_records(
        self,
        records: Iterable[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: StreamSlice,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        state_value = self.get_state_value(stream_state, stream_slice)
        filter_date = self.get_filter_date(state_value)
        records = (record for record in records if self._date_time_based_cursor.parse_date(record[self._cursor_field]) > filter_date)
        if self._delegate:
            return self._delegate.filter_records(
                records=records, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
            )
        return records

    def get_state_value(self, stream_state: StreamState, stream_slice: StreamSlice) -> Optional[str]:
        state_value = None
        if stream_state.get("states"):
            state = [
                x
                for x in stream_state.get("states", [])
                if x["partition"][self._partition_id] == stream_slice.partition[self._partition_id]
            ]
            if state:
                state_value = state[0]["cursor"][self._cursor_field]
        else:
            state_value = stream_state.get(self._cursor_field)
        return state_value

    def get_filter_date(self, state_value: Optional[str]) -> datetime.datetime:
        start_date_parsed = self._start_date_from_config or None
        state_date_parsed = self._date_time_based_cursor.parse_date(state_value) if state_value else None
        return max((x for x in (start_date_parsed, state_date_parsed) if x), default=datetime.datetime.min)
