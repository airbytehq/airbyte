#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime
from dataclasses import InitVar, dataclass
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor, PerPartitionCursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


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


class ClientSideIncrementalRecordFilterDecorator(RecordFilter):
    """
    Applies a filter to a list of records to exclude those that are older than the stream_state/start_date.

    :param DatetimeBasedCursor date_time_based_cursor: Cursor used to extract datetime values
    :param PerPartitionCursor per_partition_cursor: Optional Cursor used for mapping cursor value in nested stream_state
    """

    def __init__(
        self, date_time_based_cursor: DatetimeBasedCursor, per_partition_cursor: Optional[PerPartitionCursor] = None, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self._date_time_based_cursor = date_time_based_cursor
        self._per_partition_cursor = per_partition_cursor

    @property
    def _cursor_field(self) -> str:
        return self._date_time_based_cursor.cursor_field.eval(self._date_time_based_cursor.config)  # type: ignore # eval returns a string in this context

    @property
    def _start_date_from_config(self) -> datetime.datetime:
        return self._date_time_based_cursor._start_datetime.get_datetime(self._date_time_based_cursor.config)

    @property
    def _end_datetime(self) -> datetime.datetime:
        return self._date_time_based_cursor.select_best_end_datetime()

    def filter_records(
        self,
        records: Iterable[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        state_value = self._get_state_value(stream_state, stream_slice or StreamSlice(partition={}, cursor_slice={}))
        filter_date: datetime.datetime = self._get_filter_date(state_value)
        records = (
            record
            for record in records
            if self._end_datetime >= self._date_time_based_cursor.parse_date(record[self._cursor_field]) >= filter_date
        )
        if self.condition:
            records = super().filter_records(
                records=records, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
            )
        yield from records

    def _get_state_value(self, stream_state: StreamState, stream_slice: StreamSlice) -> Optional[str]:
        """
        Return cursor_value or None in case it was not found.
        Cursor_value may be empty if:
            1. It is an initial sync => no stream_state exist at all.
            2. In Parent-child stream, and we already make initial sync, so stream_state is present.
               During the second read, we receive one extra record from parent and therefore no stream_state for this record will be found.

        :param StreamState stream_state: State
        :param StreamSlice stream_slice: Current Stream slice
        :return Optional[str]: cursor_value in case it was found, otherwise None.
        """
        if self._per_partition_cursor:
            # self._per_partition_cursor is the same object that DeclarativeStream uses to save/update stream_state
            partition_state = self._per_partition_cursor.select_state(stream_slice=stream_slice)
            return partition_state.get(self._cursor_field) if partition_state else None
        return stream_state.get(self._cursor_field)

    def _get_filter_date(self, state_value: Optional[str]) -> datetime.datetime:
        start_date_parsed = self._start_date_from_config
        if state_value:
            return max(start_date_parsed, self._date_time_based_cursor.parse_date(state_value))
        else:
            return start_date_parsed
