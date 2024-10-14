#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from functools import partial
from typing import Any, Mapping, Optional
from unittest import TestCase
from unittest.mock import Mock

import freezegun
import pytest
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.incremental.datetime_based_cursor import DatetimeBasedCursor
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor, CursorField, CursorValueType
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import ConcurrencyCompatibleStateType
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import (
    EpochValueConcurrentStreamStateConverter,
    IsoMillisConcurrentStreamStateConverter,
)
from isodate import parse_duration

_A_STREAM_NAME = "a stream name"
_A_STREAM_NAMESPACE = "a stream namespace"
_A_CURSOR_FIELD_KEY = "a_cursor_field_key"
_NO_STATE = {}
_NO_PARTITION_IDENTIFIER = None
_NO_SLICE = None
_NO_SLICE_BOUNDARIES = None
_LOWER_SLICE_BOUNDARY_FIELD = "lower_boundary"
_UPPER_SLICE_BOUNDARY_FIELD = "upper_boundary"
_SLICE_BOUNDARY_FIELDS = (_LOWER_SLICE_BOUNDARY_FIELD, _UPPER_SLICE_BOUNDARY_FIELD)
_A_VERY_HIGH_CURSOR_VALUE = 1000000000
_NO_LOOKBACK_WINDOW = timedelta(seconds=0)


def _partition(_slice: Optional[Mapping[str, Any]], _stream_name: Optional[str] = Mock()) -> Partition:
    partition = Mock(spec=Partition)
    partition.to_slice.return_value = _slice
    partition.stream_name.return_value = _stream_name
    return partition


def _record(cursor_value: CursorValueType, partition: Optional[Partition] = Mock(spec=Partition)) -> Record:
    return Record(data={_A_CURSOR_FIELD_KEY: cursor_value}, partition=partition)


class ConcurrentCursorStateTest(TestCase):
    def setUp(self) -> None:
        self._message_repository = Mock(spec=MessageRepository)
        self._state_manager = Mock(spec=ConnectorStateManager)

    def _cursor_with_slice_boundary_fields(self, is_sequential_state=True) -> ConcurrentCursor:
        return ConcurrentCursor(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {},
            self._message_repository,
            self._state_manager,
            EpochValueConcurrentStreamStateConverter(is_sequential_state),
            CursorField(_A_CURSOR_FIELD_KEY),
            _SLICE_BOUNDARY_FIELDS,
            None,
            EpochValueConcurrentStreamStateConverter.get_end_provider(),
            _NO_LOOKBACK_WINDOW,
        )

    def _cursor_without_slice_boundary_fields(self) -> ConcurrentCursor:
        return ConcurrentCursor(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {},
            self._message_repository,
            self._state_manager,
            EpochValueConcurrentStreamStateConverter(is_sequential_state=True),
            CursorField(_A_CURSOR_FIELD_KEY),
            None,
            None,
            EpochValueConcurrentStreamStateConverter.get_end_provider(),
            _NO_LOOKBACK_WINDOW,
        )

    def test_given_boundary_fields_when_close_partition_then_emit_state(self) -> None:
        cursor = self._cursor_with_slice_boundary_fields()
        cursor.close_partition(
            _partition(
                {_LOWER_SLICE_BOUNDARY_FIELD: 12, _UPPER_SLICE_BOUNDARY_FIELD: 30},
            )
        )

        self._message_repository.emit_message.assert_called_once_with(self._state_manager.create_state_message.return_value)
        self._state_manager.update_state_for_stream.assert_called_once_with(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {_A_CURSOR_FIELD_KEY: 0},  # State message is updated to the legacy format before being emitted
        )

    def test_given_state_not_sequential_when_close_partition_then_emit_state(self) -> None:
        cursor = self._cursor_with_slice_boundary_fields(is_sequential_state=False)
        cursor.close_partition(
            _partition(
                {_LOWER_SLICE_BOUNDARY_FIELD: 12, _UPPER_SLICE_BOUNDARY_FIELD: 30},
            )
        )

        self._message_repository.emit_message.assert_called_once_with(self._state_manager.create_state_message.return_value)
        self._state_manager.update_state_for_stream.assert_called_once_with(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {"slices": [{"end": 0, "start": 0}, {"end": 30, "start": 12}], "state_type": "date-range"},
        )

    def test_close_partition_emits_message_to_lower_boundary_when_no_prior_state_exists(self) -> None:
        self._cursor_with_slice_boundary_fields().close_partition(
            _partition(
                {_LOWER_SLICE_BOUNDARY_FIELD: 0, _UPPER_SLICE_BOUNDARY_FIELD: 30},
            )
        )

        self._message_repository.emit_message.assert_called_once_with(self._state_manager.create_state_message.return_value)
        self._state_manager.update_state_for_stream.assert_called_once_with(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {_A_CURSOR_FIELD_KEY: 0},  # State message is updated to the lower slice boundary
        )

    def test_given_boundary_fields_and_record_observed_when_close_partition_then_ignore_records(self) -> None:
        cursor = self._cursor_with_slice_boundary_fields()
        cursor.observe(_record(_A_VERY_HIGH_CURSOR_VALUE))

        cursor.close_partition(_partition({_LOWER_SLICE_BOUNDARY_FIELD: 12, _UPPER_SLICE_BOUNDARY_FIELD: 30}))

        assert self._state_manager.update_state_for_stream.call_args_list[0].args[2][_A_CURSOR_FIELD_KEY] != _A_VERY_HIGH_CURSOR_VALUE

    def test_given_no_boundary_fields_when_close_partition_then_emit_state(self) -> None:
        cursor = self._cursor_without_slice_boundary_fields()
        partition = _partition(_NO_SLICE)
        cursor.observe(_record(10, partition=partition))
        cursor.close_partition(partition)

        self._state_manager.update_state_for_stream.assert_called_once_with(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {"a_cursor_field_key": 10},
        )

    def test_given_no_boundary_fields_when_close_multiple_partitions_then_raise_exception(self) -> None:
        cursor = self._cursor_without_slice_boundary_fields()
        partition = _partition(_NO_SLICE)
        cursor.observe(_record(10, partition=partition))
        cursor.close_partition(partition)

        with pytest.raises(ValueError):
            cursor.close_partition(partition)

    def test_given_no_records_observed_when_close_partition_then_do_not_emit_state(self) -> None:
        cursor = self._cursor_without_slice_boundary_fields()
        cursor.close_partition(_partition(_NO_SLICE))
        assert self._message_repository.emit_message.call_count == 0

    def test_given_slice_boundaries_and_no_slice_when_close_partition_then_raise_error(self) -> None:
        cursor = self._cursor_with_slice_boundary_fields()
        with pytest.raises(KeyError):
            cursor.close_partition(_partition(_NO_SLICE))

    def test_given_slice_boundaries_not_matching_slice_when_close_partition_then_raise_error(self) -> None:
        cursor = self._cursor_with_slice_boundary_fields()
        with pytest.raises(KeyError):
            cursor.close_partition(_partition({"not_matching_key": "value"}))

    @freezegun.freeze_time(time_to_freeze=datetime.fromtimestamp(50, timezone.utc))
    def test_given_no_state_when_generate_slices_then_create_slice_from_start_to_end(self):
        start = datetime.fromtimestamp(10, timezone.utc)
        cursor = ConcurrentCursor(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            _NO_STATE,
            self._message_repository,
            self._state_manager,
            EpochValueConcurrentStreamStateConverter(is_sequential_state=False),
            CursorField(_A_CURSOR_FIELD_KEY),
            _SLICE_BOUNDARY_FIELDS,
            start,
            EpochValueConcurrentStreamStateConverter.get_end_provider(),
            _NO_LOOKBACK_WINDOW,
        )

        slices = list(cursor.generate_slices())

        assert slices == [
            (datetime.fromtimestamp(10, timezone.utc), datetime.fromtimestamp(50, timezone.utc)),
        ]

    @freezegun.freeze_time(time_to_freeze=datetime.fromtimestamp(50, timezone.utc))
    def test_given_one_slice_when_generate_slices_then_create_slice_from_slice_upper_boundary_to_end(self):
        start = datetime.fromtimestamp(0, timezone.utc)
        cursor = ConcurrentCursor(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "slices": [
                    {EpochValueConcurrentStreamStateConverter.START_KEY: 0, EpochValueConcurrentStreamStateConverter.END_KEY: 20},
                ],
            },
            self._message_repository,
            self._state_manager,
            EpochValueConcurrentStreamStateConverter(is_sequential_state=False),
            CursorField(_A_CURSOR_FIELD_KEY),
            _SLICE_BOUNDARY_FIELDS,
            start,
            EpochValueConcurrentStreamStateConverter.get_end_provider(),
            _NO_LOOKBACK_WINDOW,
        )

        slices = list(cursor.generate_slices())

        assert slices == [
            (datetime.fromtimestamp(20, timezone.utc), datetime.fromtimestamp(50, timezone.utc)),
        ]

    @freezegun.freeze_time(time_to_freeze=datetime.fromtimestamp(50, timezone.utc))
    def test_given_start_after_slices_when_generate_slices_then_generate_from_start(self):
        start = datetime.fromtimestamp(30, timezone.utc)
        cursor = ConcurrentCursor(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "slices": [
                    {EpochValueConcurrentStreamStateConverter.START_KEY: 0, EpochValueConcurrentStreamStateConverter.END_KEY: 20},
                ],
            },
            self._message_repository,
            self._state_manager,
            EpochValueConcurrentStreamStateConverter(is_sequential_state=False),
            CursorField(_A_CURSOR_FIELD_KEY),
            _SLICE_BOUNDARY_FIELDS,
            start,
            EpochValueConcurrentStreamStateConverter.get_end_provider(),
            _NO_LOOKBACK_WINDOW,
        )

        slices = list(cursor.generate_slices())

        assert slices == [
            (datetime.fromtimestamp(30, timezone.utc), datetime.fromtimestamp(50, timezone.utc)),
        ]

    @freezegun.freeze_time(time_to_freeze=datetime.fromtimestamp(50, timezone.utc))
    def test_given_state_with_gap_and_start_after_slices_when_generate_slices_then_generate_from_start(self):
        start = datetime.fromtimestamp(30, timezone.utc)
        cursor = ConcurrentCursor(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "slices": [
                    {EpochValueConcurrentStreamStateConverter.START_KEY: 0, EpochValueConcurrentStreamStateConverter.END_KEY: 10},
                    {EpochValueConcurrentStreamStateConverter.START_KEY: 15, EpochValueConcurrentStreamStateConverter.END_KEY: 20},
                ],
            },
            self._message_repository,
            self._state_manager,
            EpochValueConcurrentStreamStateConverter(is_sequential_state=False),
            CursorField(_A_CURSOR_FIELD_KEY),
            _SLICE_BOUNDARY_FIELDS,
            start,
            EpochValueConcurrentStreamStateConverter.get_end_provider(),
            _NO_LOOKBACK_WINDOW,
        )

        slices = list(cursor.generate_slices())

        assert slices == [
            (datetime.fromtimestamp(30, timezone.utc), datetime.fromtimestamp(50, timezone.utc)),
        ]

    @freezegun.freeze_time(time_to_freeze=datetime.fromtimestamp(50, timezone.utc))
    def test_given_small_slice_range_when_generate_slices_then_create_many_slices(self):
        start = datetime.fromtimestamp(0, timezone.utc)
        small_slice_range = timedelta(seconds=10)
        cursor = ConcurrentCursor(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "slices": [
                    {EpochValueConcurrentStreamStateConverter.START_KEY: 0, EpochValueConcurrentStreamStateConverter.END_KEY: 20},
                ],
            },
            self._message_repository,
            self._state_manager,
            EpochValueConcurrentStreamStateConverter(is_sequential_state=False),
            CursorField(_A_CURSOR_FIELD_KEY),
            _SLICE_BOUNDARY_FIELDS,
            start,
            EpochValueConcurrentStreamStateConverter.get_end_provider(),
            _NO_LOOKBACK_WINDOW,
            small_slice_range,
        )

        slices = list(cursor.generate_slices())

        assert slices == [
            (datetime.fromtimestamp(20, timezone.utc), datetime.fromtimestamp(30, timezone.utc)),
            (datetime.fromtimestamp(30, timezone.utc), datetime.fromtimestamp(40, timezone.utc)),
            (datetime.fromtimestamp(40, timezone.utc), datetime.fromtimestamp(50, timezone.utc)),
        ]

    @freezegun.freeze_time(time_to_freeze=datetime.fromtimestamp(50, timezone.utc))
    def test_given_difference_between_slices_match_slice_range_when_generate_slices_then_create_one_slice(self):
        start = datetime.fromtimestamp(0, timezone.utc)
        small_slice_range = timedelta(seconds=10)
        cursor = ConcurrentCursor(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "slices": [
                    {EpochValueConcurrentStreamStateConverter.START_KEY: 0, EpochValueConcurrentStreamStateConverter.END_KEY: 30},
                    {EpochValueConcurrentStreamStateConverter.START_KEY: 40, EpochValueConcurrentStreamStateConverter.END_KEY: 50},
                ],
            },
            self._message_repository,
            self._state_manager,
            EpochValueConcurrentStreamStateConverter(is_sequential_state=False),
            CursorField(_A_CURSOR_FIELD_KEY),
            _SLICE_BOUNDARY_FIELDS,
            start,
            EpochValueConcurrentStreamStateConverter.get_end_provider(),
            _NO_LOOKBACK_WINDOW,
            small_slice_range,
        )

        slices = list(cursor.generate_slices())

        assert slices == [
            (datetime.fromtimestamp(30, timezone.utc), datetime.fromtimestamp(40, timezone.utc)),
        ]

    @freezegun.freeze_time(time_to_freeze=datetime.fromtimestamp(50, timezone.utc))
    def test_given_non_continuous_state_when_generate_slices_then_create_slices_between_gaps_and_after(self):
        cursor = ConcurrentCursor(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "slices": [
                    {EpochValueConcurrentStreamStateConverter.START_KEY: 0, EpochValueConcurrentStreamStateConverter.END_KEY: 10},
                    {EpochValueConcurrentStreamStateConverter.START_KEY: 20, EpochValueConcurrentStreamStateConverter.END_KEY: 25},
                    {EpochValueConcurrentStreamStateConverter.START_KEY: 30, EpochValueConcurrentStreamStateConverter.END_KEY: 40},
                ],
            },
            self._message_repository,
            self._state_manager,
            EpochValueConcurrentStreamStateConverter(is_sequential_state=False),
            CursorField(_A_CURSOR_FIELD_KEY),
            _SLICE_BOUNDARY_FIELDS,
            None,
            EpochValueConcurrentStreamStateConverter.get_end_provider(),
            _NO_LOOKBACK_WINDOW,
        )

        slices = list(cursor.generate_slices())

        assert slices == [
            (datetime.fromtimestamp(10, timezone.utc), datetime.fromtimestamp(20, timezone.utc)),
            (datetime.fromtimestamp(25, timezone.utc), datetime.fromtimestamp(30, timezone.utc)),
            (datetime.fromtimestamp(40, timezone.utc), datetime.fromtimestamp(50, timezone.utc)),
        ]

    @freezegun.freeze_time(time_to_freeze=datetime.fromtimestamp(50, timezone.utc))
    def test_given_lookback_window_when_generate_slices_then_apply_lookback_on_most_recent_slice(self):
        start = datetime.fromtimestamp(0, timezone.utc)
        lookback_window = timedelta(seconds=10)
        cursor = ConcurrentCursor(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "slices": [
                    {EpochValueConcurrentStreamStateConverter.START_KEY: 0, EpochValueConcurrentStreamStateConverter.END_KEY: 20},
                    {EpochValueConcurrentStreamStateConverter.START_KEY: 30, EpochValueConcurrentStreamStateConverter.END_KEY: 40},
                ],
            },
            self._message_repository,
            self._state_manager,
            EpochValueConcurrentStreamStateConverter(is_sequential_state=False),
            CursorField(_A_CURSOR_FIELD_KEY),
            _SLICE_BOUNDARY_FIELDS,
            start,
            EpochValueConcurrentStreamStateConverter.get_end_provider(),
            lookback_window,
        )

        slices = list(cursor.generate_slices())

        assert slices == [
            (datetime.fromtimestamp(20, timezone.utc), datetime.fromtimestamp(30, timezone.utc)),
            (datetime.fromtimestamp(30, timezone.utc), datetime.fromtimestamp(50, timezone.utc)),
        ]

    @freezegun.freeze_time(time_to_freeze=datetime.fromtimestamp(50, timezone.utc))
    def test_given_start_is_before_first_slice_lower_boundary_when_generate_slices_then_generate_slice_before(self):
        start = datetime.fromtimestamp(0, timezone.utc)
        cursor = ConcurrentCursor(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "slices": [
                    {EpochValueConcurrentStreamStateConverter.START_KEY: 10, EpochValueConcurrentStreamStateConverter.END_KEY: 20},
                ],
            },
            self._message_repository,
            self._state_manager,
            EpochValueConcurrentStreamStateConverter(is_sequential_state=False),
            CursorField(_A_CURSOR_FIELD_KEY),
            _SLICE_BOUNDARY_FIELDS,
            start,
            EpochValueConcurrentStreamStateConverter.get_end_provider(),
            _NO_LOOKBACK_WINDOW,
        )

        slices = list(cursor.generate_slices())

        assert slices == [
            (datetime.fromtimestamp(0, timezone.utc), datetime.fromtimestamp(10, timezone.utc)),
            (datetime.fromtimestamp(20, timezone.utc), datetime.fromtimestamp(50, timezone.utc)),
        ]


@freezegun.freeze_time(time_to_freeze=datetime(2024, 4, 1, 0, 0, 0, 0, tzinfo=timezone.utc))
@pytest.mark.parametrize(
    "start_datetime,end_datetime,step,cursor_field,lookback_window,state,expected_slices",
    [
        pytest.param(
            "{{ config.start_time }}",
            "{{ config.end_time or now_utc() }}",
            "P10D",
            "updated_at",
            "P5D",
            {},
            [
                (datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc), datetime(2024, 1, 10, 23, 59, 59, tzinfo=timezone.utc)),
                (datetime(2024, 1, 11, 0, 0, tzinfo=timezone.utc), datetime(2024, 1, 20, 23, 59, 59, tzinfo=timezone.utc)),
                (datetime(2024, 1, 21, 0, 0, tzinfo=timezone.utc), datetime(2024, 1, 30, 23, 59, 59, tzinfo=timezone.utc)),
                (datetime(2024, 1, 31, 0, 0, tzinfo=timezone.utc), datetime(2024, 2, 9, 23, 59, 59, tzinfo=timezone.utc)),
                (datetime(2024, 2, 10, 0, 0, tzinfo=timezone.utc), datetime(2024, 2, 19, 23, 59, 59, tzinfo=timezone.utc)),
                (datetime(2024, 2, 20, 0, 0, tzinfo=timezone.utc), datetime(2024, 2, 29, 23, 59, 59, tzinfo=timezone.utc))
            ],
            id="test_datetime_based_cursor_all_fields",
        ),
        pytest.param(
            "{{ config.start_time }}",
            "{{ config.end_time or '2024-01-01T00:00:00.000000+0000' }}",
            "P10D",
            "updated_at",
            "P5D",
            {
                "slices": [
                    {
                        "start": "2024-01-01T00:00:00.000000+0000",
                        "end": "2024-02-10T00:00:00.000000+0000",
                    }
                ],
                "state_type": "date-range"
            },
            [
                (datetime(2024, 2, 5, 0, 0, 0, tzinfo=timezone.utc), datetime(2024, 2, 14, 23, 59, 59, tzinfo=timezone.utc)),
                (datetime(2024, 2, 15, 0, 0, 0, tzinfo=timezone.utc), datetime(2024, 2, 24, 23, 59, 59, tzinfo=timezone.utc)),
                (datetime(2024, 2, 25, 0, 0, 0, tzinfo=timezone.utc), datetime(2024, 2, 29, 23, 59, 59, tzinfo=timezone.utc))
            ],
            id="test_datetime_based_cursor_with_state",
        ),
        pytest.param(
            "{{ config.start_time }}",
            "{{ config.missing or now_utc().strftime('%Y-%m-%dT%H:%M:%S.%fZ') }}",
            "P20D",
            "updated_at",
            "P1D",
            {
                "slices": [
                    {
                        "start": "2024-01-01T00:00:00.000000+0000",
                        "end": "2024-01-21T00:00:00.000000+0000",
                    }
                ],
                "state_type": "date-range"
            },
            [
                (datetime(2024, 1, 20, 0, 0, tzinfo=timezone.utc), datetime(2024, 2, 8, 23, 59, 59, tzinfo=timezone.utc)),
                (datetime(2024, 2, 9, 0, 0, tzinfo=timezone.utc), datetime(2024, 2, 28, 23, 59, 59, tzinfo=timezone.utc)),
                (datetime(2024, 2, 29, 0, 0, tzinfo=timezone.utc), datetime(2024, 3, 19, 23, 59, 59, tzinfo=timezone.utc)),
                (datetime(2024, 3, 20, 0, 0, tzinfo=timezone.utc), datetime(2024, 3, 31, 23, 59, 59, tzinfo=timezone.utc)),
            ],
            id="test_datetime_based_cursor_with_state_and_end_date",
        ),
        pytest.param(
            "{{ config.start_time }}",
            "{{ config.end_time }}",
            "P1M",
            "updated_at",
            "P5D",
            {},
            [
                (datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc), datetime(2024, 1, 31, 23, 59, 59, tzinfo=timezone.utc)),
                (datetime(2024, 2, 1, 0, 0, 0, tzinfo=timezone.utc), datetime(2024, 2, 29, 23, 59, 59, tzinfo=timezone.utc)),
            ],
            id="test_datetime_based_cursor_using_large_step_duration",
        ),
    ]
)
def test_generate_slices_concurrent_cursor_from_datetime_based_cursor(
    start_datetime,
    end_datetime,
    step,
    cursor_field,
    lookback_window,
    state,
    expected_slices,
):
    message_repository = Mock(spec=MessageRepository)
    state_manager = Mock(spec=ConnectorStateManager)

    config = {
        "start_time": "2024-01-01T00:00:00.000000+0000",
        "end_time": "2024-03-01T00:00:00.000000+0000",
    }

    datetime_based_cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime(datetime=start_datetime, parameters={}),
        end_datetime=MinMaxDatetime(datetime=end_datetime, parameters={}),
        step=step,
        cursor_field=cursor_field,
        partition_field_start="start",
        partition_field_end="end",
        datetime_format="%Y-%m-%dT%H:%M:%S.%f%z",
        cursor_granularity="PT1S",
        lookback_window=lookback_window,
        is_compare_strictly=True,
        config=config,
        parameters={},
    )

    # I don't love that we're back to this inching close to interpolation at parse time instead of runtime
    # We also might need to add a wrapped class that exposes these fields publicly or live with ugly private access
    interpolated_state_date = datetime_based_cursor._start_datetime
    start_date = interpolated_state_date.get_datetime(config=config)

    interpolated_end_date = datetime_based_cursor._end_datetime
    interpolated_end_date_provider = partial(interpolated_end_date.get_datetime, config)

    interpolated_cursor_field = datetime_based_cursor.cursor_field
    cursor_field = CursorField(cursor_field_key=interpolated_cursor_field.eval(config=config))

    lower_slice_boundary = datetime_based_cursor._partition_field_start.eval(config=config)
    upper_slice_boundary = datetime_based_cursor._partition_field_end.eval(config=config)
    slice_boundary_fields = (lower_slice_boundary, upper_slice_boundary)

    # DatetimeBasedCursor returns an isodate.Duration if step uses month or year precision. This still works in our
    # code, but mypy may complain when we actually implement this in the concurrent low-code source. To fix this, we
    # may need to convert a Duration to timedelta by multiplying month by 30 (but could lose precision).
    step_length = datetime_based_cursor._step

    lookback_window = parse_duration(datetime_based_cursor.lookback_window) if datetime_based_cursor.lookback_window else None

    cursor_granularity = parse_duration(datetime_based_cursor.cursor_granularity) if datetime_based_cursor.cursor_granularity else None

    cursor = ConcurrentCursor(
        stream_name=_A_STREAM_NAME,
        stream_namespace=_A_STREAM_NAMESPACE,
        stream_state=state,
        message_repository=message_repository,
        connector_state_manager=state_manager,
        connector_state_converter=IsoMillisConcurrentStreamStateConverter(is_sequential_state=True),
        cursor_field=cursor_field,
        slice_boundary_fields=slice_boundary_fields,
        start=start_date,
        end_provider=interpolated_end_date_provider,
        lookback_window=lookback_window,
        slice_range=step_length,
        cursor_granularity=cursor_granularity,
    )

    actual_slices = list(cursor.generate_slices())
    assert actual_slices == expected_slices


@freezegun.freeze_time(time_to_freeze=datetime(2024, 9, 1, 0, 0, 0, 0, tzinfo=timezone.utc))
def test_observe_concurrent_cursor_from_datetime_based_cursor():
    message_repository = Mock(spec=MessageRepository)
    state_manager = Mock(spec=ConnectorStateManager)

    config = {
        "start_time": "2024-08-01T00:00:00.000000+0000",
        "dynamic_cursor_key": "updated_at"
    }

    datetime_based_cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime(datetime="{{ config.start_time }}", parameters={}),
        cursor_field="{{ config.dynamic_cursor_key }}",
        datetime_format="%Y-%m-%dT%H:%M:%S.%f%z",
        config=config,
        parameters={},
    )

    interpolated_state_date = datetime_based_cursor._start_datetime
    start_date = interpolated_state_date.get_datetime(config=config)

    interpolated_cursor_field = datetime_based_cursor.cursor_field
    cursor_field = CursorField(cursor_field_key=interpolated_cursor_field.eval(config=config))

    step_length = datetime_based_cursor._step

    concurrent_cursor = ConcurrentCursor(
        stream_name="gods",
        stream_namespace=_A_STREAM_NAMESPACE,
        stream_state={},
        message_repository=message_repository,
        connector_state_manager=state_manager,
        connector_state_converter=IsoMillisConcurrentStreamStateConverter(is_sequential_state=True),
        cursor_field=cursor_field,
        slice_boundary_fields=None,
        start=start_date,
        end_provider=IsoMillisConcurrentStreamStateConverter.get_end_provider(),
        slice_range=step_length,
    )

    partition = _partition(
        {_LOWER_SLICE_BOUNDARY_FIELD: "2024-08-01T00:00:00.000000+0000", _UPPER_SLICE_BOUNDARY_FIELD: "2024-09-01T00:00:00.000000+0000"},
        _stream_name="gods",
    )

    record_1 = Record(
        partition=partition, data={"id": "999", "updated_at": "2024-08-23T00:00:00.000000+0000", "name": "kratos", "mythology": "greek"},
    )
    record_2 = Record(
        partition=partition, data={"id": "1000", "updated_at": "2024-08-22T00:00:00.000000+0000", "name": "odin", "mythology": "norse"},
    )
    record_3 = Record(
        partition=partition, data={"id": "500", "updated_at": "2024-08-24T00:00:00.000000+0000", "name": "freya", "mythology": "norse"},
    )

    concurrent_cursor.observe(record_1)
    actual_most_recent_record = concurrent_cursor._most_recent_cursor_value_per_partition[partition]
    assert actual_most_recent_record == concurrent_cursor._extract_cursor_value(record_1)

    concurrent_cursor.observe(record_2)
    actual_most_recent_record = concurrent_cursor._most_recent_cursor_value_per_partition[partition]
    assert actual_most_recent_record == concurrent_cursor._extract_cursor_value(record_1)

    concurrent_cursor.observe(record_3)
    actual_most_recent_record = concurrent_cursor._most_recent_cursor_value_per_partition[partition]
    assert actual_most_recent_record == concurrent_cursor._extract_cursor_value(record_3)


@freezegun.freeze_time(time_to_freeze=datetime(2024, 9, 1, 0, 0, 0, 0, tzinfo=timezone.utc))
def test_close_partition_concurrent_cursor_from_datetime_based_cursor():
    message_repository = Mock(spec=MessageRepository)
    state_manager = Mock(spec=ConnectorStateManager)

    config = {
        "start_time": "2024-08-01T00:00:00.000000+0000",
        "dynamic_cursor_key": "updated_at"
    }

    datetime_based_cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime(datetime="{{ config.start_time }}", parameters={}),
        cursor_field="{{ config.dynamic_cursor_key }}",
        datetime_format="%Y-%m-%dT%H:%M:%S.%f%z",
        config=config,
        parameters={},
    )

    interpolated_state_date = datetime_based_cursor._start_datetime
    start_date = interpolated_state_date.get_datetime(config=config)

    interpolated_cursor_field = datetime_based_cursor.cursor_field
    cursor_field = CursorField(cursor_field_key=interpolated_cursor_field.eval(config=config))

    step_length = datetime_based_cursor._step

    concurrent_cursor = ConcurrentCursor(
        stream_name="gods",
        stream_namespace=_A_STREAM_NAMESPACE,
        stream_state={},
        message_repository=message_repository,
        connector_state_manager=state_manager,
        connector_state_converter=IsoMillisConcurrentStreamStateConverter(is_sequential_state=False),
        cursor_field=cursor_field,
        slice_boundary_fields=None,
        start=start_date,
        end_provider=IsoMillisConcurrentStreamStateConverter.get_end_provider(),
        slice_range=step_length,
    )

    partition = _partition(
        {_LOWER_SLICE_BOUNDARY_FIELD: "2024-08-01T00:00:00.000000+0000", _UPPER_SLICE_BOUNDARY_FIELD: "2024-09-01T00:00:00.000000+0000"},
        _stream_name="gods",
    )

    record_1 = Record(
        partition=partition, data={"id": "999", "updated_at": "2024-08-23T00:00:00.000000+0000", "name": "kratos", "mythology": "greek"},
    )
    concurrent_cursor.observe(record_1)

    concurrent_cursor.close_partition(partition)

    message_repository.emit_message.assert_called_once_with(state_manager.create_state_message.return_value)
    state_manager.update_state_for_stream.assert_called_once_with(
        "gods",
        _A_STREAM_NAMESPACE,
        {
            "slices": [{"end": "2024-08-23T00:00:00.000Z", "start": "2024-08-01T00:00:00.000Z"}],
            "state_type": "date-range"
        },
    )


@freezegun.freeze_time(time_to_freeze=datetime(2024, 9, 1, 0, 0, 0, 0, tzinfo=timezone.utc))
def test_close_partition_with_slice_range_concurrent_cursor_from_datetime_based_cursor():
    message_repository = Mock(spec=MessageRepository)
    state_manager = Mock(spec=ConnectorStateManager)

    config = {
        "start_time": "2024-07-01T00:00:00.000000+0000",
        "dynamic_cursor_key": "updated_at"
    }

    datetime_based_cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime(datetime="{{ config.start_time }}", parameters={}),
        cursor_field="{{ config.dynamic_cursor_key }}",
        datetime_format="%Y-%m-%dT%H:%M:%S.%f%z",
        step="P15D",
        cursor_granularity="P1D",
        config=config,
        parameters={},
    )

    interpolated_state_date = datetime_based_cursor._start_datetime
    start_date = interpolated_state_date.get_datetime(config=config)

    interpolated_cursor_field = datetime_based_cursor.cursor_field
    cursor_field = CursorField(cursor_field_key=interpolated_cursor_field.eval(config=config))

    lower_slice_boundary = datetime_based_cursor._partition_field_start.eval(config=config)
    upper_slice_boundary = datetime_based_cursor._partition_field_end.eval(config=config)
    slice_boundary_fields = (lower_slice_boundary, upper_slice_boundary)

    step_length = datetime_based_cursor._step

    concurrent_cursor = ConcurrentCursor(
        stream_name="gods",
        stream_namespace=_A_STREAM_NAMESPACE,
        stream_state={},
        message_repository=message_repository,
        connector_state_manager=state_manager,
        connector_state_converter=IsoMillisConcurrentStreamStateConverter(is_sequential_state=False, cursor_granularity=None),
        cursor_field=cursor_field,
        slice_boundary_fields=slice_boundary_fields,
        start=start_date,
        slice_range=step_length,
        cursor_granularity=None,
        end_provider=IsoMillisConcurrentStreamStateConverter.get_end_provider(),
    )

    partition_0 = _partition(
        {"start_time": "2024-07-01T00:00:00.000000+0000", "end_time": "2024-07-16T00:00:00.000000+0000"}, _stream_name="gods",
    )
    partition_3 = _partition(
        {"start_time": "2024-08-15T00:00:00.000000+0000", "end_time": "2024-08-30T00:00:00.000000+0000"}, _stream_name="gods",
    )
    record_1 = Record(
        partition=partition_0, data={"id": "1000", "updated_at": "2024-07-05T00:00:00.000000+0000", "name": "loki", "mythology": "norse"},
    )
    record_2 = Record(
        partition=partition_3, data={"id": "999", "updated_at": "2024-08-20T00:00:00.000000+0000", "name": "kratos", "mythology": "greek"},
    )

    concurrent_cursor.observe(record_1)
    concurrent_cursor.close_partition(partition_0)
    concurrent_cursor.observe(record_2)
    concurrent_cursor.close_partition(partition_3)

    message_repository.emit_message.assert_called_with(state_manager.create_state_message.return_value)
    assert message_repository.emit_message.call_count == 2
    state_manager.update_state_for_stream.assert_called_with(
        "gods",
        _A_STREAM_NAMESPACE,
        {
            "slices": [
                {"start": "2024-07-01T00:00:00.000Z", "end": "2024-07-16T00:00:00.000Z"},
                {"start": "2024-08-15T00:00:00.000Z", "end": "2024-08-30T00:00:00.000Z"}

            ],
            "state_type": "date-range"
        },
    )
    assert state_manager.update_state_for_stream.call_count == 2


@freezegun.freeze_time(time_to_freeze=datetime(2024, 9, 1, 0, 0, 0, 0, tzinfo=timezone.utc))
def test_close_partition_with_slice_range_granularity_concurrent_cursor_from_datetime_based_cursor():
    message_repository = Mock(spec=MessageRepository)
    state_manager = Mock(spec=ConnectorStateManager)

    config = {
        "start_time": "2024-07-01T00:00:00.000000+0000",
        "dynamic_cursor_key": "updated_at"
    }

    datetime_based_cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime(datetime="{{ config.start_time }}", parameters={}),
        cursor_field="{{ config.dynamic_cursor_key }}",
        datetime_format="%Y-%m-%dT%H:%M:%S.%f%z",
        step="P15D",
        cursor_granularity="P1D",
        config=config,
        parameters={},
    )

    interpolated_state_date = datetime_based_cursor._start_datetime
    start_date = interpolated_state_date.get_datetime(config=config)

    interpolated_cursor_field = datetime_based_cursor.cursor_field
    cursor_field = CursorField(cursor_field_key=interpolated_cursor_field.eval(config=config))

    lower_slice_boundary = datetime_based_cursor._partition_field_start.eval(config=config)
    upper_slice_boundary = datetime_based_cursor._partition_field_end.eval(config=config)
    slice_boundary_fields = (lower_slice_boundary, upper_slice_boundary)

    step_length = datetime_based_cursor._step

    cursor_granularity = parse_duration(datetime_based_cursor.cursor_granularity) if datetime_based_cursor.cursor_granularity else None

    concurrent_cursor = ConcurrentCursor(
        stream_name="gods",
        stream_namespace=_A_STREAM_NAMESPACE,
        stream_state={},
        message_repository=message_repository,
        connector_state_manager=state_manager,
        connector_state_converter=IsoMillisConcurrentStreamStateConverter(is_sequential_state=False, cursor_granularity=cursor_granularity),
        cursor_field=cursor_field,
        slice_boundary_fields=slice_boundary_fields,
        start=start_date,
        slice_range=step_length,
        cursor_granularity=cursor_granularity,
        end_provider=IsoMillisConcurrentStreamStateConverter.get_end_provider(),
    )

    partition_0 = _partition(
        {"start_time": "2024-07-01T00:00:00.000000+0000", "end_time": "2024-07-15T00:00:00.000000+0000"}, _stream_name="gods",
    )
    partition_1 = _partition(
        {"start_time": "2024-07-16T00:00:00.000000+0000", "end_time": "2024-07-31T00:00:00.000000+0000"}, _stream_name="gods",
    )
    partition_3 = _partition(
        {"start_time": "2024-08-15T00:00:00.000000+0000", "end_time": "2024-08-29T00:00:00.000000+0000"}, _stream_name="gods",
    )
    record_1 = Record(
        partition=partition_0, data={"id": "1000", "updated_at": "2024-07-05T00:00:00.000000+0000", "name": "loki", "mythology": "norse"},
    )
    record_2 = Record(
        partition=partition_1, data={"id": "2000", "updated_at": "2024-07-25T00:00:00.000000+0000", "name": "freya", "mythology": "norse"},
    )
    record_3 = Record(
        partition=partition_3, data={"id": "999", "updated_at": "2024-08-20T00:00:00.000000+0000", "name": "kratos", "mythology": "greek"},
    )

    concurrent_cursor.observe(record_1)
    concurrent_cursor.close_partition(partition_0)
    concurrent_cursor.observe(record_2)
    concurrent_cursor.close_partition(partition_1)
    concurrent_cursor.observe(record_3)
    concurrent_cursor.close_partition(partition_3)

    message_repository.emit_message.assert_called_with(state_manager.create_state_message.return_value)
    assert message_repository.emit_message.call_count == 3
    state_manager.update_state_for_stream.assert_called_with(
        "gods",
        _A_STREAM_NAMESPACE,
        {
            "slices": [
                {"start": "2024-07-01T00:00:00.000Z", "end": "2024-07-31T00:00:00.000Z"},
                {"start": "2024-08-15T00:00:00.000Z", "end": "2024-08-29T00:00:00.000Z"}

            ],
            "state_type": "date-range"
        },
    )
    assert state_manager.update_state_for_stream.call_count == 3
