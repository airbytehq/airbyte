#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import functools
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Mapping, MutableMapping, Optional, Protocol, Tuple

from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams import FULL_REFRESH_SENTINEL_STATE_KEY
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
    @property
    @abstractmethod
    def state(self) -> MutableMapping[str, Any]:
        ...

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
    def ensure_at_least_one_state_emitted(self) -> None:
        """
        State messages are emitted when a partition is closed. However, the platform expects at least one state to be emitted per sync per
        stream. Hence, if no partitions are generated, this method needs to be called.
        """
        raise NotImplementedError()


class FinalStateCursor(Cursor):
    """Cursor that is used to guarantee at least one state message is emitted for a concurrent stream."""

    def __init__(
        self,
        stream_name: str,
        stream_namespace: Optional[str],
        message_repository: MessageRepository,
    ) -> None:
        self._stream_name = stream_name
        self._stream_namespace = stream_namespace
        self._message_repository = message_repository
        # Normally the connector state manager operates at the source-level. However, we only need it to write the sentinel
        # state message rather than manage overall source state. This is also only temporary as we move to the resumable
        # full refresh world where every stream uses a FileBasedConcurrentCursor with incremental state.
        self._connector_state_manager = ConnectorStateManager(stream_instance_map={})
        self._has_closed_at_least_one_slice = False

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {FULL_REFRESH_SENTINEL_STATE_KEY: True}

    def observe(self, record: Record) -> None:
        pass

    def close_partition(self, partition: Partition) -> None:
        pass

    def ensure_at_least_one_state_emitted(self) -> None:
        """
        Used primarily for full refresh syncs that do not have a valid cursor value to emit at the end of a sync
        """

        self._connector_state_manager.update_state_for_stream(self._stream_name, self._stream_namespace, self.state)
        state_message = self._connector_state_manager.create_state_message(self._stream_name, self._stream_namespace)
        self._message_repository.emit_message(state_message)


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
        start: Optional[Any],
    ) -> None:
        self._stream_name = stream_name
        self._stream_namespace = stream_namespace
        self._message_repository = message_repository
        self._connector_state_converter = connector_state_converter
        self._connector_state_manager = connector_state_manager
        self._cursor_field = cursor_field
        # To see some example where the slice boundaries might not be defined, check https://github.com/airbytehq/airbyte/blob/1ce84d6396e446e1ac2377362446e3fb94509461/airbyte-integrations/connectors/source-stripe/source_stripe/streams.py#L363-L379
        self._slice_boundary_fields = slice_boundary_fields if slice_boundary_fields else tuple()
        self._start = start
        self._most_recent_record: Optional[Record] = None
        self._has_closed_at_least_one_slice = False
        self.start, self._concurrent_state = self._get_concurrent_state(stream_state)

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._concurrent_state

    def _get_concurrent_state(self, state: MutableMapping[str, Any]) -> Tuple[datetime, MutableMapping[str, Any]]:
        if self._connector_state_converter.is_state_message_compatible(state):
            return self._start or self._connector_state_converter.zero_value, self._connector_state_converter.deserialize(state)
        return self._connector_state_converter.convert_from_sequential_state(self._cursor_field, state, self._start)

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
        slice_count_before = len(self.state.get("slices", []))
        self._add_slice_to_state(partition)
        if slice_count_before < len(self.state["slices"]):  # only emit if at least one slice has been processed
            self._merge_partitions()
            self._emit_state_message()
        self._has_closed_at_least_one_slice = True

    def _add_slice_to_state(self, partition: Partition) -> None:
        if self._slice_boundary_fields:
            if "slices" not in self.state:
                raise RuntimeError(
                    f"The state for stream {self._stream_name} should have at least one slice to delineate the sync start time, but no slices are present. This is unexpected. Please contact Support."
                )
            self.state["slices"].append(
                {
                    "start": self._extract_from_slice(partition, self._slice_boundary_fields[self._START_BOUNDARY]),
                    "end": self._extract_from_slice(partition, self._slice_boundary_fields[self._END_BOUNDARY]),
                }
            )
        elif self._most_recent_record:
            if self._has_closed_at_least_one_slice:
                # If we track state value using records cursor field, we can only do that if there is one partition. This is because we save
                # the state every time we close a partition. We assume that if there are multiple slices, they need to be providing
                # boundaries. There are cases where partitions could not have boundaries:
                # * The cursor should be per-partition
                # * The stream state is actually the parent stream state
                # There might be other cases not listed above. Those are not supported today hence the stream should not use this cursor for
                # state management. For the specific user that was affected with this issue, we need to:
                # * Fix state tracking (which is currently broken)
                # * Make the new version available
                # * (Probably) ask the user to reset the stream to avoid data loss
                raise ValueError(
                    "Given that slice_boundary_fields is not defined and that per-partition state is not supported, only one slice is "
                    "expected. Please contact the Airbyte team."
                )

            self.state["slices"].append(
                {
                    self._connector_state_converter.START_KEY: self.start,
                    self._connector_state_converter.END_KEY: self._extract_cursor_value(self._most_recent_record),
                }
            )

    def _emit_state_message(self) -> None:
        self._connector_state_manager.update_state_for_stream(
            self._stream_name,
            self._stream_namespace,
            self._connector_state_converter.convert_to_sequential_state(self._cursor_field, self.state),
        )
        # TODO: if we migrate stored state to the concurrent state format
        #  (aka stop calling self._connector_state_converter.convert_to_sequential_state`), we'll need to cast datetimes to string or
        #  int before emitting state
        state_message = self._connector_state_manager.create_state_message(self._stream_name, self._stream_namespace)
        self._message_repository.emit_message(state_message)

    def _merge_partitions(self) -> None:
        self.state["slices"] = self._connector_state_converter.merge_intervals(self.state["slices"])

    def _extract_from_slice(self, partition: Partition, key: str) -> Comparable:
        try:
            _slice = partition.to_slice()
            if not _slice:
                raise KeyError(f"Could not find key `{key}` in empty slice")
            return self._connector_state_converter.parse_value(_slice[key])  # type: ignore  # we expect the devs to specify a key that would return a Comparable
        except KeyError as exception:
            raise KeyError(f"Partition is expected to have key `{key}` but could not be found") from exception

    def ensure_at_least_one_state_emitted(self) -> None:
        """
        The platform expect to have at least one state message on successful syncs. Hence, whatever happens, we expect this method to be
        called.
        """
        self._emit_state_message()
