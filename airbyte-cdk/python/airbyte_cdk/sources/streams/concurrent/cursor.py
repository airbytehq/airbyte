#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import functools
from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Protocol, Tuple

from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams import NO_CURSOR_STATE_KEY
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import AbstractStreamStateConverter


def _extract_value(mapping: Mapping[str, Any], path: List[str]) -> Any:
    return functools.reduce(lambda a, b: a[b], path, mapping)


class GapType(Protocol):
    """
    This is the representation of gaps between two cursor values. Examples:
    * if cursor values are datetimes, GapType is timedelta
    * if cursor values are integer, GapType will also be integer
    """

    pass


class CursorValueType(Protocol):
    """Protocol for annotating comparable types."""

    @abstractmethod
    def __lt__(self: "CursorValueType", other: "CursorValueType") -> bool:
        pass

    @abstractmethod
    def __ge__(self: "CursorValueType", other: "CursorValueType") -> bool:
        pass

    @abstractmethod
    def __add__(self: "CursorValueType", other: GapType) -> "CursorValueType":
        pass

    @abstractmethod
    def __sub__(self: "CursorValueType", other: GapType) -> "CursorValueType":
        pass


class CursorField:
    def __init__(self, cursor_field_key: str) -> None:
        self.cursor_field_key = cursor_field_key

    def extract_value(self, record: Record) -> CursorValueType:
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

    def generate_slices(self) -> Iterable[Tuple[Any, Any]]:
        """
        Default placeholder implementation of generate_slices.
        Subclasses can override this method to provide actual behavior.
        """
        yield from ()


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
        self._connector_state_manager = ConnectorStateManager()
        self._has_closed_at_least_one_slice = False

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {NO_CURSOR_STATE_KEY: True}

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
        start: Optional[CursorValueType],
        end_provider: Callable[[], CursorValueType],
        lookback_window: Optional[GapType] = None,
        slice_range: Optional[GapType] = None,
        cursor_granularity: Optional[GapType] = None,
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
        self._end_provider = end_provider
        self.start, self._concurrent_state = self._get_concurrent_state(stream_state)
        self._lookback_window = lookback_window
        self._slice_range = slice_range
        self._most_recent_cursor_value_per_partition: MutableMapping[Partition, Any] = {}
        self._has_closed_at_least_one_slice = False
        self._cursor_granularity = cursor_granularity

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._concurrent_state

    def _get_concurrent_state(self, state: MutableMapping[str, Any]) -> Tuple[CursorValueType, MutableMapping[str, Any]]:
        if self._connector_state_converter.is_state_message_compatible(state):
            return self._start or self._connector_state_converter.zero_value, self._connector_state_converter.deserialize(state)
        return self._connector_state_converter.convert_from_sequential_state(self._cursor_field, state, self._start)

    def observe(self, record: Record) -> None:
        most_recent_cursor_value = self._most_recent_cursor_value_per_partition.get(record.partition)
        cursor_value = self._extract_cursor_value(record)

        if most_recent_cursor_value is None or most_recent_cursor_value < cursor_value:
            self._most_recent_cursor_value_per_partition[record.partition] = cursor_value

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
        most_recent_cursor_value = self._most_recent_cursor_value_per_partition.get(partition)

        if self._slice_boundary_fields:
            if "slices" not in self.state:
                raise RuntimeError(
                    f"The state for stream {self._stream_name} should have at least one slice to delineate the sync start time, but no slices are present. This is unexpected. Please contact Support."
                )
            self.state["slices"].append(
                {
                    self._connector_state_converter.START_KEY: self._extract_from_slice(
                        partition, self._slice_boundary_fields[self._START_BOUNDARY]
                    ),
                    self._connector_state_converter.END_KEY: self._extract_from_slice(
                        partition, self._slice_boundary_fields[self._END_BOUNDARY]
                    ),
                    "most_recent_cursor_value": most_recent_cursor_value,
                }
            )
        elif most_recent_cursor_value:
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
                    self._connector_state_converter.END_KEY: most_recent_cursor_value,
                    "most_recent_cursor_value": most_recent_cursor_value,
                }
            )

    def _emit_state_message(self) -> None:
        self._connector_state_manager.update_state_for_stream(
            self._stream_name,
            self._stream_namespace,
            self._connector_state_converter.convert_to_state_message(self._cursor_field, self.state),
        )
        state_message = self._connector_state_manager.create_state_message(self._stream_name, self._stream_namespace)
        self._message_repository.emit_message(state_message)

    def _merge_partitions(self) -> None:
        self.state["slices"] = self._connector_state_converter.merge_intervals(self.state["slices"])

    def _extract_from_slice(self, partition: Partition, key: str) -> CursorValueType:
        try:
            _slice = partition.to_slice()
            if not _slice:
                raise KeyError(f"Could not find key `{key}` in empty slice")
            return self._connector_state_converter.parse_value(_slice[key])  # type: ignore  # we expect the devs to specify a key that would return a CursorValueType
        except KeyError as exception:
            raise KeyError(f"Partition is expected to have key `{key}` but could not be found") from exception

    def ensure_at_least_one_state_emitted(self) -> None:
        """
        The platform expect to have at least one state message on successful syncs. Hence, whatever happens, we expect this method to be
        called.
        """
        self._emit_state_message()

    def generate_slices(self) -> Iterable[Tuple[CursorValueType, CursorValueType]]:
        """
        Generating slices based on a few parameters:
        * lookback_window: Buffer to remove from END_KEY of the highest slice
        * slice_range: Max difference between two slices. If the difference between two slices is greater, multiple slices will be created
        * start: `_split_per_slice_range` will clip any value to `self._start which means that:
          * if upper is less than self._start, no slices will be generated
          * if lower is less than self._start, self._start will be used as the lower boundary (lookback_window will not be considered in that case)

        Note that the slices will overlap at their boundaries. We therefore expect to have at least the lower or the upper boundary to be
        inclusive in the API that is queried.
        """
        self._merge_partitions()

        if self._start is not None and self._is_start_before_first_slice():
            yield from self._split_per_slice_range(self._start, self.state["slices"][0][self._connector_state_converter.START_KEY])

        if len(self.state["slices"]) == 1:
            yield from self._split_per_slice_range(
                self._calculate_lower_boundary_of_last_slice(self.state["slices"][0][self._connector_state_converter.END_KEY]),
                self._end_provider(),
            )
        elif len(self.state["slices"]) > 1:
            for i in range(len(self.state["slices"]) - 1):
                yield from self._split_per_slice_range(
                    self.state["slices"][i][self._connector_state_converter.END_KEY],
                    self.state["slices"][i + 1][self._connector_state_converter.START_KEY],
                )
            yield from self._split_per_slice_range(
                self._calculate_lower_boundary_of_last_slice(self.state["slices"][-1][self._connector_state_converter.END_KEY]),
                self._end_provider(),
            )
        else:
            raise ValueError("Expected at least one slice")

    def _is_start_before_first_slice(self) -> bool:
        return self._start is not None and self._start < self.state["slices"][0][self._connector_state_converter.START_KEY]

    def _calculate_lower_boundary_of_last_slice(self, lower_boundary: CursorValueType) -> CursorValueType:
        if self._lookback_window:
            return lower_boundary - self._lookback_window
        return lower_boundary

    def _split_per_slice_range(self, lower: CursorValueType, upper: CursorValueType) -> Iterable[Tuple[CursorValueType, CursorValueType]]:
        if lower >= upper:
            return

        if self._start and upper < self._start:
            return

        lower = max(lower, self._start) if self._start else lower
        if not self._slice_range or lower + self._slice_range >= upper:
            yield lower, upper
        else:
            stop_processing = False
            current_lower_boundary = lower
            while not stop_processing:
                current_upper_boundary = min(current_lower_boundary + self._slice_range, upper)
                if self._cursor_granularity:
                    yield current_lower_boundary, current_upper_boundary - self._cursor_granularity
                else:
                    yield current_lower_boundary, current_upper_boundary
                current_lower_boundary = current_upper_boundary
                if current_upper_boundary >= upper:
                    stop_processing = True
