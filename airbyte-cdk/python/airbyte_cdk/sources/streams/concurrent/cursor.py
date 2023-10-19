import functools
from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Optional, Protocol, Tuple

from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager


def _extract_value(mapping: Mapping[str, Any], path: List[str]) -> Any:
    return functools.reduce(lambda a, b: a[b], path, mapping)


class Comparable(Protocol):
    """Protocol for annotating comparable types."""

    @abstractmethod
    def __lt__(self: "Comparable", other: "Comparable") -> bool:
        pass


class CursorField:
    def __init__(self, path: List[str]) -> None:
        self._path = path

    def extract_value(self, record: Record) -> Comparable:
        return _extract_value(record.data, self._path)  # type: ignore  # we assume that the value the path points at is a comparable


class Cursor(ABC):

    @abstractmethod
    def observe(self, record: Record) -> None:
        raise NotImplementedError()

    @abstractmethod
    def close_partition(self, partition: Partition) -> None:
        raise NotImplementedError()


class NoopCursor(Cursor):
    def observe(self, record: Record) -> None:
        pass

    def close_partition(self, partition: Partition) -> None:
        pass


class ConcurrentCursor(Cursor):
    # FIXME add unit tests
    _START_BOUNDARY = 0
    _END_BOUNDARY = 1

    def __init__(self, stream_name: str, stream_namespace: str, stream_state: Any, message_repository: MessageRepository, connector_state_manager: ConnectorStateManager, cursor_field: CursorField, slice_boundary_fields: Optional[Tuple[str]]) -> None:
        self._stream_name = stream_name
        self._stream_namespace = stream_namespace
        self._message_repository = message_repository
        self._connector_state_manager = connector_state_manager
        self._cursor_field = cursor_field
        self._slice_boundary_fields = slice_boundary_fields if slice_boundary_fields else tuple()
        self._most_recent_record = None

        # TODO to migrate state. The migration should probably be outside of this class. Impact of not having this:
        #  * Given a sync that emits no records, the emitted state message will be empty
        self._state = {
          "slices": [
            #{start: 1, end: 10, parent_id: "id1", finished_processing: true},
          ]
        }

    def observe(self, record: Record) -> None:
        if self._slice_boundary_fields:
            # Given that slicing is done using the cursor field, we don't need to observe the record as slices will describe what has been
            # emitted. Assuming there is a chance that records might not be yet populated for the most recent slice, use lookback window
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

    def _add_slice_to_state(self, partition) -> None:
        partition_identifier = partition.identifier() or {}
        if self._slice_boundary_fields:
            self._state["slices"].append({
                "start": self._extract_from_slice(partition, self._slice_boundary_fields[self._START_BOUNDARY]),
                "end": self._extract_from_slice(partition, self._slice_boundary_fields[self._END_BOUNDARY]),
                **partition_identifier,
            })
        elif self._most_recent_record:
            # State is observed by records and not by slices
            self._state["slices"].append({
                "start": 0,  # FIXME this only works with int datetime
                "end": self._extract_cursor_value(self._most_recent_record),
                **partition_identifier,
            })

    def _emit_state_message(self) -> None:
        self._connector_state_manager.update_state_for_stream(self._stream_name, self._stream_namespace, self._state)
        state_message = self._connector_state_manager.create_state_message(
            self._stream_name,
            self._stream_namespace,
            send_per_stream_state=True
        )
        self._message_repository.emit_message(state_message)

    def _merge_partitions(self):
        pass  # TODO eventually

    def _extract_from_slice(self, partition: Partition, key: str):
        return partition.to_slice()[key]
