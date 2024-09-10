#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Optional
from unittest import TestCase
from unittest.mock import Mock

import freezegun
import pytest
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor, CursorField, CursorValueType
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import ConcurrencyCompatibleStateType
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import EpochValueConcurrentStreamStateConverter

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


def _partition(_slice: Optional[Mapping[str, Any]]) -> Partition:
    partition = Mock(spec=Partition)
    partition.to_slice.return_value = _slice
    return partition


def _record(cursor_value: CursorValueType) -> Record:
    return Record(data={_A_CURSOR_FIELD_KEY: cursor_value}, stream_name=_A_STREAM_NAME)


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

    def test_given_boundary_fields_when_close_partition_then_emit_updated_state(self) -> None:
        self._cursor_with_slice_boundary_fields().close_partition(
            _partition(
                {_LOWER_SLICE_BOUNDARY_FIELD: 0, _UPPER_SLICE_BOUNDARY_FIELD: 30},
            )
        )

        self._message_repository.emit_message.assert_called_once_with(self._state_manager.create_state_message.return_value)
        self._state_manager.update_state_for_stream.assert_called_once_with(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {_A_CURSOR_FIELD_KEY: 30},  # State message is updated to the legacy format before being emitted
        )

    def test_given_boundary_fields_and_record_observed_when_close_partition_then_ignore_records(self) -> None:
        cursor = self._cursor_with_slice_boundary_fields()
        cursor.observe(_record(_A_VERY_HIGH_CURSOR_VALUE))

        cursor.close_partition(_partition({_LOWER_SLICE_BOUNDARY_FIELD: 12, _UPPER_SLICE_BOUNDARY_FIELD: 30}))

        assert self._state_manager.update_state_for_stream.call_args_list[0].args[2][_A_CURSOR_FIELD_KEY] != _A_VERY_HIGH_CURSOR_VALUE

    def test_given_no_boundary_fields_when_close_partition_then_emit_state(self) -> None:
        cursor = self._cursor_without_slice_boundary_fields()
        cursor.observe(_record(10))
        cursor.close_partition(_partition(_NO_SLICE))

        self._state_manager.update_state_for_stream.assert_called_once_with(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {"a_cursor_field_key": 10},
        )

    def test_given_no_boundary_fields_when_close_multiple_partitions_then_raise_exception(self) -> None:
        cursor = self._cursor_without_slice_boundary_fields()
        cursor.observe(_record(10))
        cursor.close_partition(_partition(_NO_SLICE))

        with pytest.raises(ValueError):
            cursor.close_partition(_partition(_NO_SLICE))

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
