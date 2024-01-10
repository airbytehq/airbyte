#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import functools
from abc import ABC, abstractmethod
from threading import Lock
from typing import Any, List, Mapping, Optional, Protocol, Set, Tuple

from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import AbstractStreamStateConverter


def _extract_value(mapping: Mapping[str, Any], path: List[str]) -> Any:
    return functools.reduce(lambda a, b: a[b], path, mapping)


class Comparable(Protocol):
    """Protocol for annotating comparable types."""

    @abstractmethod
    def __lt__(self: "Comparable", other: "Comparable") -> bool:
        pass


class CursorField:
    def __init__(self, cursor_field_key: str) -> None:
        self.cursor_field_key = cursor_field_key

    def extract_value(self, record: Record) -> Comparable:
        cursor_value = record.data.get(self.cursor_field_key)
        if cursor_value is None:
            raise ValueError(f"Could not find cursor field {self.cursor_field_key} in record")
        return cursor_value  # type: ignore  # we assume that the value the path points at is a comparable


class Cursor(ABC):
    @abstractmethod
    def observe(self, record: Record) -> None:
        """
        Indicate to the cursor that the record has been emitted
        """
        raise NotImplementedError()

    @abstractmethod
    def close_partition(self, partition: Partition) -> None:
        """
        Indicate to the cursor that the partition has been successfully processed
        """
        raise NotImplementedError()

    @abstractmethod
    def set_pending_partitions(self, pending_partitions: List[Partition]):
        """
        Set the pending partitions for tracking the job state
        """
        ...


class NoopCursor(Cursor):
    def observe(self, record: Record) -> None:
        pass

    def close_partition(self, partition: Partition) -> None:
        pass


class ConcurrentCursor(Cursor):
    _START_BOUNDARY = 0
    _END_BOUNDARY = 1

    def __init__(
        self,
        stream_name: str,
        stream_namespace: Optional[str],
        stream_state: Any,
        message_repository: MessageRepository,
        connector_state_manager: ConnectorStateManager,
        connector_state_converter: AbstractStreamStateConverter,
        cursor_field: CursorField,
        slice_boundary_fields: Optional[Tuple[str, str]],
    ) -> None:
        self._stream_name = stream_name
        self._stream_namespace = stream_namespace
        self._message_repository = message_repository
        self._connector_state_converter = connector_state_converter
        self._connector_state_manager = connector_state_manager
        self._cursor_field = cursor_field
        # To see some example where the slice boundaries might not be defined, check https://github.com/airbytehq/airbyte/blob/1ce84d6396e446e1ac2377362446e3fb94509461/airbyte-integrations/connectors/source-stripe/source_stripe/streams.py#L363-L379
        self._slice_boundary_fields = slice_boundary_fields if slice_boundary_fields else tuple()
        self._most_recent_record: Optional[Record] = None
        self._has_closed_at_least_one_slice = False
        self.state = stream_state
        self._pending_slices = None
        self._min = None

    def set_pending_partitions(self, pending_partitions: List[Partition]):
        """
        Set the slices waiting to be processed.

        Also sets the min value of all slices for use in updating the state's `low_water_mark`.
        """
        pending_slices = set()
        for partition in pending_partitions:
            pending_slices.add(self._get_key_from_partition(partition))
        if pending_slices:
            _first_interval = sorted(pending_slices, key=lambda x: (x[self._START_BOUNDARY], x[self._END_BOUNDARY]))[0]
            self._min = _first_interval[self._START_BOUNDARY]
        self._pending_slices = pending_slices

    def _get_key_from_partition(self, partition: Partition):
        partition_slice = partition.to_slice()
        return (
            self._connector_state_converter.parse_value(partition_slice[self._connector_state_converter.START_KEY]),
            self._connector_state_converter.parse_value(partition_slice[self._connector_state_converter.END_KEY]),
        )

    def observe(self, record: Record) -> None:
        if self._slice_boundary_fields:
            # Given that slicing is done using the cursor field, we don't need to observe the record as we assume slices will describe what
            # has been emitted. Assuming there is a chance that records might not be yet populated for the most recent slice, use a lookback
            # window
            return

        if not self._most_recent_record or self._extract_cursor_value(self._most_recent_record) < self._extract_cursor_value(record):
            self._most_recent_record = record

    def _extract_cursor_value(self, record: Record) -> Any:
        return self._connector_state_converter.parse_value(self._cursor_field.extract_value(record))

    def close_partition(self, partition: Partition) -> None:
        """
        Closes partitions and advances the low_water_mark if appropriate.

        When a close_partition request comes in, we pop the partition from the set of pending partitions.
        We then use the timestamp of the earliest partition as the new "low water mark" - the time before which all partitions have been processed.

        # Start
        [(1,2), (3,4), (5,6), (6,7)]
        _min = 1
        low_water_mark = None
        no partitions are complete
        emitted state = <min>

        # (5,6) finishes
        [(1,2) (3,4), (6,7)]
        low_water_mark = 1*

        # (1,2) finishes
        [(3,4), (6,7)]
        low_water_mark = 3 - increment

        # (6,7) finishes
        [3,4]
        low_water_mark = 3 - increment

        # (3,4) finishes
        []
        low_water_mark = max(min, last_slice_end)

        *To avoid decrementing the cursor in the case where no partitions finish, we
        take the max(_min, low_water_mark - increment)
        """
        if not self._min:
            raise RuntimeError(f"The cursor's `_min` value should be set before processing partitions, but was not. This is unexpected. Please contact support.")

        position_before = self.state["low_water_mark"]
        partition_key = self._get_key_from_partition(partition)
        self._pending_slices -= {partition_key}
        converter = self._connector_state_converter

        if self._pending_slices:
            self.state["low_water_mark"] = converter.max(
            converter.decrement(converter.min([start for start, end in self._pending_slices])),
                self._min,
            )
        else:
            # We are done processing all partitions
            partition_slice = partition.to_slice()
            self.state["low_water_mark"] = partition_key[-1]

        position_after = self.state["low_water_mark"]

        if self._has_advanced(position_before, position_after):
            self._emit_state_message()
        self._has_closed_at_least_one_slice = True

    def _has_advanced(self, before, after) -> bool:
        return self._connector_state_converter.is_greater_than(after, before)

    def _emit_state_message(self) -> None:
        self._connector_state_manager.update_state_for_stream(
            self._stream_name,
            self._stream_namespace,
            self._connector_state_converter.convert_to_sequential_state(self._cursor_field, self.state),
        )
        # TODO: if we migrate stored state to the concurrent state format
        #  (aka stop calling self._connector_state_converter.convert_to_sequential_state`), we'll need to cast datetimes to string or
        #  int before emitting state
        state_message = self._connector_state_manager.create_state_message(
            self._stream_name, self._stream_namespace, send_per_stream_state=True
        )
        self._message_repository.emit_message(state_message)

    def _extract_from_slice(self, partition: Partition, key: str) -> Comparable:
        try:
            _slice = partition.to_slice()
            if not _slice:
                raise KeyError(f"Could not find key `{key}` in empty slice for {partition.stream_name()}")
            return self._connector_state_converter.parse_value(_slice[key])  # type: ignore  # we expect the devs to specify a key that would return a Comparable
        except KeyError as exception:
            raise KeyError(f"Partition is expected to have key `{key}` but could not be found in {partition.stream_name()} {partition.to_slice()}") from exception
