#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import datetime
import threading
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

from isodate import Duration, parse_duration

from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.declarative.datetime.datetime_parser import DatetimeParser
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.models import DatetimeBasedCursor as DatetimeBasedCursorModel
from airbyte_cdk.sources.declarative.models import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.models import MinMaxDatetime as MinMaxDatetimeModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.partition_routers import PartitionRouter
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor, CursorField
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.types import Config, Record, StreamSlice


EVENTS_STREAM_NAME = "events"
PROJECT_ID_FIELD = "project_id"

_SliceKey = Tuple[str, str, str]


@dataclass
class _SliceProgress:
    """Records read for one slice, and whether the slice has been read to the end."""

    has_records: bool = False
    most_recent_cursor_value: str = ""
    closed: bool = False


class EventsPerProjectCursor(Cursor):
    """Cursor of the `events` stream, which keeps one timestamp per project.

    The state has the same shape as in every earlier version of the connector:
    {
        "project_id1": {
          "timestamp": "2021-02-01T10:21:35.003000Z"
        },
        "project_idX": {
          "timestamp": "2022-11-17:00:00.000000Z"
        }
    }
    It also accepts the old-style (before 0.1.8) state, which applies one timestamp to every project:
    {
        "timestamp": "2021-17-01T10:21:35.003000Z"
    }

    Each project gets its own datetime slices, which start from that project's timestamp. A project that has no
    timestamp in the state, for example a project created after the last sync, starts from the configured start date
    (or from the old-style timestamp, if the state has one).

    The partitions of the stream are read concurrently, so slices can finish out of order. A project's timestamp only
    moves forward once all of its earlier slices have finished, so that a failed slice is read again on the next sync.
    """

    def __init__(
        self,
        stream_name: str,
        partition_router: PartitionRouter,
        start_datetime: MinMaxDatetime,
        end_datetime: Optional[MinMaxDatetime],
        step: Union[datetime.timedelta, Duration],
        cursor_granularity: datetime.timedelta,
        datetime_format: str,
        cursor_datetime_formats: List[str],
        config: Config,
        stream_state: Optional[Mapping[str, Any]],
        message_repository: MessageRepository,
        connector_state_manager: ConnectorStateManager,
        cursor_field: str = "timestamp",
        partition_field_start: str = "start_time",
        partition_field_end: str = "end_time",
    ) -> None:
        self._stream_name = stream_name
        self._partition_router = partition_router
        self._start_datetime = start_datetime
        self._end_datetime = end_datetime
        self._step = step
        self._cursor_granularity = cursor_granularity
        self._datetime_format = datetime_format
        self._cursor_datetime_formats = cursor_datetime_formats
        self._config = config
        self._message_repository = message_repository
        self._connector_state_manager = connector_state_manager
        self._cursor_field = CursorField(cursor_field)
        self._partition_field_start = partition_field_start
        self._partition_field_end = partition_field_end
        self._parser = DatetimeParser()

        # Slices are computed from the incoming state, never from the state updated during the sync.
        self._initial_state: Mapping[str, Any] = copy.deepcopy(dict(stream_state or {}))
        self._state: MutableMapping[str, Any] = copy.deepcopy(dict(stream_state or {}))

        self._lock = threading.Lock()
        # Slices of each project, in the order they were generated, that are not yet applied to the state.
        self._pending_slices: Dict[str, Deque[_SliceProgress]] = {}
        # Slices being read, by slice key. A queue keeps the lookup unambiguous should a slice be generated twice.
        self._open_slices: Dict[_SliceKey, Deque[_SliceProgress]] = {}

    @property
    def cursor_field(self) -> CursorField:
        return self._cursor_field

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    def stream_slices(self) -> Iterable[StreamSlice]:
        # Support of old-style state: it only contains a single 'timestamp' field
        old_style_state = self._initial_state if self._cursor_field.cursor_field_key in self._initial_state else {}

        for project_slice in self._partition_router.stream_slices():
            project_id = str(project_slice.get(PROJECT_ID_FIELD, ""))

            # Use the old-style state if the state has no timestamp for this project
            project_state = self._initial_state.get(project_id, {}) or old_style_state

            for datetime_slice in self._project_datetime_slices(project_state):
                stream_slice = StreamSlice(partition={PROJECT_ID_FIELD: project_id}, cursor_slice=datetime_slice)
                self._register_slice(stream_slice)
                yield stream_slice

    def _project_datetime_slices(self, project_state: Mapping[str, Any]) -> List[Dict[str, str]]:
        cursor_value = project_state.get(self._cursor_field.cursor_field_key) if project_state else None

        end_datetime = self._select_best_end_datetime()
        earliest_possible_start = min(self._start_datetime.get_datetime(self._config), end_datetime)
        cursor_datetime = self._parse_date(cursor_value) if cursor_value else datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
        start = max(earliest_possible_start, cursor_datetime)

        slices = []
        while start <= end_datetime:
            next_start = self._evaluate_next_start_date_safely(start)
            slice_end = min(next_start - self._cursor_granularity, end_datetime)
            slices.append({self._partition_field_start: self._format_date(start), self._partition_field_end: self._format_date(slice_end)})
            start = next_start

        # Fix date ranges: the first slice starts exactly at the state value,
        # and the start of each next slice is equal to the end of the previous slice
        if slices and project_state:
            slices[0][self._partition_field_start] = project_state[self._cursor_field.cursor_field_key]
        for i in range(1, len(slices)):
            slices[i][self._partition_field_start] = slices[i - 1][self._partition_field_end]

        return slices

    def _select_best_end_datetime(self) -> datetime.datetime:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        if not self._end_datetime:
            return now
        return min(self._end_datetime.get_datetime(self._config), now)

    def _evaluate_next_start_date_safely(self, start: datetime.datetime) -> datetime.datetime:
        try:
            return start + self._step
        except OverflowError:
            return datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)

    def _parse_date(self, date: str) -> datetime.datetime:
        for datetime_format in self._cursor_datetime_formats + [self._datetime_format]:
            try:
                return self._parser.parse(date, datetime_format)
            except ValueError:
                pass
        raise ValueError(f"No format in {self._cursor_datetime_formats} matching {date}")

    def _format_date(self, value: datetime.datetime) -> str:
        return self._parser.format(value, self._datetime_format)

    def _slice_key(self, stream_slice: Optional[Mapping[str, Any]]) -> Optional[_SliceKey]:
        if not stream_slice:
            return None
        return (
            str(stream_slice.get(PROJECT_ID_FIELD, "")),
            str(stream_slice.get(self._partition_field_start, "")),
            str(stream_slice.get(self._partition_field_end, "")),
        )

    def _register_slice(self, stream_slice: StreamSlice) -> None:
        key = self._slice_key(stream_slice)
        progress = _SliceProgress()
        with self._lock:
            self._pending_slices.setdefault(key[0], deque()).append(progress)
            self._open_slices.setdefault(key, deque()).append(progress)

    def observe(self, record: Record) -> None:
        key = self._slice_key(record.associated_slice)
        with self._lock:
            open_slices = self._open_slices.get(key) if key else None
            if not open_slices:
                return
            progress = open_slices[0]
            progress.has_records = True
            record_cursor_value = record.data.get(self._cursor_field.cursor_field_key)
            if record_cursor_value and record_cursor_value > progress.most_recent_cursor_value:
                progress.most_recent_cursor_value = record_cursor_value

    def close_partition(self, partition: Partition) -> None:
        key = self._slice_key(partition.to_slice())
        with self._lock:
            open_slices = self._open_slices.get(key) if key else None
            if open_slices:
                open_slices.popleft().closed = True
                if not open_slices:
                    del self._open_slices[key]
                self._apply_closed_slices(key[0])
            self._emit_state_message()

    def _apply_closed_slices(self, project_id: str) -> None:
        pending = self._pending_slices.get(project_id)
        while pending and pending[0].closed:
            progress = pending.popleft()
            if project_id and progress.has_records:
                current_cursor_value = self._state.get(project_id, {}).get(self._cursor_field.cursor_field_key, "")
                self._state[project_id] = {
                    self._cursor_field.cursor_field_key: max(current_cursor_value, progress.most_recent_cursor_value)
                }

    def ensure_at_least_one_state_emitted(self) -> None:
        with self._lock:
            self._emit_state_message()

    def _emit_state_message(self) -> None:
        self._connector_state_manager.update_state_for_stream(self._stream_name, None, copy.deepcopy(self._state))
        state_message = self._connector_state_manager.create_state_message(self._stream_name, None)
        self._message_repository.emit_message(state_message)

    def should_be_synced(self, record: Record) -> bool:
        # The API filters the events by the slice boundaries, so there is nothing to filter on the client side.
        return True


class PosthogModelToComponentFactory(ModelToComponentFactory):
    """Builds the `events` stream with `EventsPerProjectCursor` instead of the per-partition cursor of the CDK.

    The manifest declares the `events` stream with a `SubstreamPartitionRouter` over projects and a
    `DatetimeBasedCursor`. The CDK would turn that into a `ConcurrentPerPartitionCursor`, which writes a different state
    format and starts a project that is new since the last sync from the latest timestamp of the other projects, instead
    of from the start date. `EventsPerProjectCursor` keeps the state format and behavior of the connector, and reuses the
    `DatetimeBasedCursor` definition, so the CDK still injects the `after`/`before` request parameters from each slice.
    """

    def _build_concurrent_cursor(
        self,
        model: DeclarativeStreamModel,
        stream_slicer: Optional[PartitionRouter],
        config: Config,
    ) -> Cursor:
        if model.name == EVENTS_STREAM_NAME and isinstance(model.incremental_sync, DatetimeBasedCursorModel) and stream_slicer:
            return self._create_events_cursor(model.incremental_sync, stream_slicer, config)
        return super()._build_concurrent_cursor(model, stream_slicer, config)

    def _create_events_cursor(
        self, cursor_model: DatetimeBasedCursorModel, partition_router: PartitionRouter, config: Config
    ) -> EventsPerProjectCursor:
        parameters = cursor_model.parameters or {}

        def _min_max_datetime(value: Union[str, MinMaxDatetimeModel]) -> MinMaxDatetime:
            min_max_datetime = MinMaxDatetime.create(
                self.create_min_max_datetime(value, config) if isinstance(value, MinMaxDatetimeModel) else value, parameters
            )
            if not min_max_datetime.datetime_format:
                min_max_datetime.datetime_format = cursor_model.datetime_format
            return min_max_datetime

        step = InterpolatedString.create(cursor_model.step, parameters=parameters).eval(config) if cursor_model.step else None
        return EventsPerProjectCursor(
            stream_name=EVENTS_STREAM_NAME,
            partition_router=partition_router,
            start_datetime=_min_max_datetime(cursor_model.start_datetime),
            end_datetime=_min_max_datetime(cursor_model.end_datetime) if cursor_model.end_datetime else None,
            step=parse_duration(step) if step else datetime.timedelta.max,
            cursor_granularity=parse_duration(cursor_model.cursor_granularity)
            if cursor_model.cursor_granularity
            else datetime.timedelta(0),
            datetime_format=cursor_model.datetime_format,
            cursor_datetime_formats=list(cursor_model.cursor_datetime_formats or []),
            config=config,
            stream_state=self._connector_state_manager.get_stream_state(EVENTS_STREAM_NAME, None),
            message_repository=self._message_repository,
            connector_state_manager=self._connector_state_manager,
            cursor_field=InterpolatedString.create(cursor_model.cursor_field, parameters=parameters).eval(config),
        )
