#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Any, Mapping, Optional
from unittest import TestCase
from unittest.mock import Mock

import pytest
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.cursor import Comparable, ConcurrentCursor, CursorField
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import EpochValueConcurrentStreamStateConverter

_A_STREAM_NAME = "a stream name"
_A_STREAM_NAMESPACE = "a stream namespace"
_A_CURSOR_FIELD_KEY = "a_cursor_field_key"
_NO_PARTITION_IDENTIFIER = None
_NO_SLICE = None
_NO_SLICE_BOUNDARIES = None
_LOWER_SLICE_BOUNDARY_FIELD = "lower_boundary"
_UPPER_SLICE_BOUNDARY_FIELD = "upper_boundary"
_SLICE_BOUNDARY_FIELDS = (_LOWER_SLICE_BOUNDARY_FIELD, _UPPER_SLICE_BOUNDARY_FIELD)
_A_VERY_HIGH_CURSOR_VALUE = 1000000000


def _partition(_slice: Optional[Mapping[str, Any]]) -> Partition:
    partition = Mock(spec=Partition)
    partition.to_slice.return_value = _slice
    return partition


def _record(cursor_value: Comparable) -> Record:
    return Record(data={_A_CURSOR_FIELD_KEY: cursor_value}, stream_name=_A_STREAM_NAME)


class ConcurrentCursorTest(TestCase):
    def setUp(self) -> None:
        self._message_repository = Mock(spec=MessageRepository)
        self._state_manager = Mock(spec=ConnectorStateManager)
        self._state_converter = EpochValueConcurrentStreamStateConverter()

    def _cursor_with_slice_boundary_fields(self) -> ConcurrentCursor:
        return ConcurrentCursor(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {},
            self._message_repository,
            self._state_manager,
            self._state_converter,
            CursorField(_A_CURSOR_FIELD_KEY),
            _SLICE_BOUNDARY_FIELDS,
            None,
        )

    def _cursor_without_slice_boundary_fields(self) -> ConcurrentCursor:
        return ConcurrentCursor(
            _A_STREAM_NAME,
            _A_STREAM_NAMESPACE,
            {},
            self._message_repository,
            self._state_manager,
            self._state_converter,
            CursorField(_A_CURSOR_FIELD_KEY),
            None,
            None,
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
