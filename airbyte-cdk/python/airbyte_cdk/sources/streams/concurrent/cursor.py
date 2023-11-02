#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import functools
from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Optional, Protocol, Tuple

from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.state_converter import ConcurrentStreamStateConverter


def _extract_value(mapping: Mapping[str, Any], path: List[str]) -> Any:
    return functools.reduce(lambda a, b: a[b], path, mapping)


class Comparable(Protocol):
    """Protocol for annotating comparable types."""

    @abstractmethod
    def __lt__(self: "Comparable", other: "Comparable") -> bool:
        pass


class CursorField:
    def __init__(self, cursor_field_key: str) -> None:
        self._cursor_field_key = cursor_field_key

    def extract_value(self, record: Record) -> Comparable:
        cursor_value = record.data.get(self._cursor_field_key)
        if cursor_value is None:
            raise ValueError(f"Could not find cursor field {self._cursor_field_key} in record")
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
        connector_state_converter: ConcurrentStreamStateConverter,
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
        self._state = connector_state_converter.get_concurrent_stream_state(stream_state)

    def observe(self, record: Record) -> None:
        if self._slice_boundary_fields:
            # Given that slicing is done using the cursor field, we don't need to observe the record as we assume slices will describe what
            # has been emitted. Assuming there is a chance that records might not be yet populated for the most recent slice, use a lookback
            # window
            return

        if not self._most_recent_record or self._extract_cursor_value(self._most_recent_record) < self._extract_cursor_value(record):
            self._most_recent_record = record

    def _extract_cursor_value(self, record: Record) -> Comparable:
        return self._cursor_field.extract_value(record)

    def close_partition(self, partition: Partition) -> None:
        slice_count_before = len(self._state["slices"])
        self._add_slice_to_state(partition)
        if slice_count_before < len(self._state["slices"]):
            self._merge_partitions()
            self._emit_state_message()
        self._has_closed_at_least_one_slice = True

    def _add_slice_to_state(self, partition: Partition) -> None:
        if self._slice_boundary_fields:
            if "slices" not in self._state:
                self._state["slices"] = []
            self._state["slices"].append(
                {
                    "start": self._extract_from_slice(partition, self._slice_boundary_fields[self._START_BOUNDARY]),
                    "end": self._extract_from_slice(partition, self._slice_boundary_fields[self._END_BOUNDARY]),
                }
            )
        elif self._most_recent_record:
            if self._has_closed_at_least_one_slice:
                raise ValueError(
                    "Given that slice_boundary_fields is not defined and that per-partition state is not supported, only one slice is "
                    "expected."
                )

            self._state["slices"].append(
                {
                    "start": 0,  # FIXME this only works with int datetime
                    "end": self._extract_cursor_value(self._most_recent_record),
                }
            )

    def _emit_state_message(self) -> None:
        self._connector_state_manager.update_state_for_stream(self._stream_name, self._stream_namespace, self._state)
        state_message = self._connector_state_manager.create_state_message(
            self._stream_name, self._stream_namespace, send_per_stream_state=True
        )
        self._message_repository.emit_message(state_message)

    def _merge_partitions(self) -> None:
        self._state["slices"] = self._connector_state_converter.merge_intervals(self._state["slices"])

    def _extract_from_slice(self, partition: Partition, key: str) -> Comparable:
        try:
            _slice = partition.to_slice()
            if not _slice:
                raise KeyError(f"Could not find key `{key}` in empty slice")
            return _slice[key]  # type: ignore  # we expect the devs to specify a key that would return a Comparable
        except KeyError as exception:
            raise KeyError(f"Partition is expected to have key `{key}` but could not be found") from exception
