#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import functools
import logging
import threading
from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
)

from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import MessageRepository, NoopMessageRepository
from airbyte_cdk.sources.streams import NO_CURSOR_STATE_KEY
from airbyte_cdk.sources.streams.concurrent.clamping import ClampingStrategy, NoClamping
from airbyte_cdk.sources.streams.concurrent.cursor_types import CursorValueType, GapType
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.stream_slicer import StreamSlicer
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import (
    AbstractStreamStateConverter,
)
from airbyte_cdk.sources.types import Record, StreamSlice

LOGGER = logging.getLogger("airbyte")


def _extract_value(mapping: Mapping[str, Any], path: List[str]) -> Any:
    return functools.reduce(lambda a, b: a[b], path, mapping)


class CursorField:
    def __init__(self, cursor_field_key: str) -> None:
        self.cursor_field_key = cursor_field_key

    def extract_value(self, record: Record) -> Any:
        cursor_value = record.data.get(self.cursor_field_key)
        if cursor_value is None:
            raise ValueError(f"Could not find cursor field {self.cursor_field_key} in record")
        return cursor_value  # type: ignore  # we assume that the value the path points at is a comparable


class Cursor(StreamSlicer, ABC):
    @property
    @abstractmethod
    def state(self) -> MutableMapping[str, Any]: ...

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

    @abstractmethod
    def should_be_synced(self, record: Record) -> bool:
        pass

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Default placeholder implementation of generate_slices.
        Subclasses can override this method to provide actual behavior.
        """
        yield StreamSlice(partition={}, cursor_slice={})


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

        self._connector_state_manager.update_state_for_stream(
            self._stream_name, self._stream_namespace, self.state
        )
        state_message = self._connector_state_manager.create_state_message(
            self._stream_name, self._stream_namespace
        )
        self._message_repository.emit_message(state_message)

    def should_be_synced(self, record: Record) -> bool:
        return True


class ConcurrentCursor(Cursor):
    _START_BOUNDARY = 0
    _END_BOUNDARY = 1

    def copy_without_state(self) -> "ConcurrentCursor":
        return self.__class__(
            stream_name=self._stream_name,
            stream_namespace=self._stream_namespace,
            stream_state={},
            message_repository=NoopMessageRepository(),
            connector_state_manager=ConnectorStateManager(),
            connector_state_converter=self._connector_state_converter,
            cursor_field=self._cursor_field,
            slice_boundary_fields=self._slice_boundary_fields,
            start=self._start,
            end_provider=self._end_provider,
            lookback_window=self._lookback_window,
            slice_range=self._slice_range,
            cursor_granularity=self._cursor_granularity,
            clamping_strategy=self._clamping_strategy,
        )

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
        clamping_strategy: ClampingStrategy = NoClamping(),
    ) -> None:
        self._stream_name = stream_name
        self._stream_namespace = stream_namespace
        self._message_repository = message_repository
        self._connector_state_converter = connector_state_converter
        self._connector_state_manager = connector_state_manager
        self._cursor_field = cursor_field
        # To see some example where the slice boundaries might not be defined, check https://github.com/airbytehq/airbyte/blob/1ce84d6396e446e1ac2377362446e3fb94509461/airbyte-integrations/connectors/source-stripe/source_stripe/streams.py#L363-L379
        self._slice_boundary_fields = slice_boundary_fields
        self._start = start
        self._end_provider = end_provider
        self.start, self._concurrent_state = self._get_concurrent_state(stream_state)
        self._lookback_window = lookback_window
        self._slice_range = slice_range
        self._most_recent_cursor_value_per_partition: MutableMapping[
            Union[StreamSlice, Mapping[str, Any], None], Any
        ] = {}
        self._has_closed_at_least_one_slice = False
        self._cursor_granularity = cursor_granularity
        # Flag to track if the logger has been triggered (per stream)
        self._should_be_synced_logger_triggered = False
        self._clamping_strategy = clamping_strategy
        self._is_ascending_order = True

        # A lock is required when closing a partition because updating the cursor's concurrent_state is
        # not thread safe. When multiple partitions are being closed by the cursor at the same time, it is
        # possible for one partition to update concurrent_state after a second partition has already read
        # the previous state. This can lead to the second partition overwriting the previous one's state.
        self._lock = threading.Lock()

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._connector_state_converter.convert_to_state_message(
            self.cursor_field, self._concurrent_state
        )

    @property
    def cursor_field(self) -> CursorField:
        return self._cursor_field

    @property
    def _slice_boundary_fields_wrapper(self) -> Tuple[str, str]:
        return (
            self._slice_boundary_fields
            if self._slice_boundary_fields
            else (
                self._connector_state_converter.START_KEY,
                self._connector_state_converter.END_KEY,
            )
        )

    def _get_concurrent_state(
        self, state: MutableMapping[str, Any]
    ) -> Tuple[CursorValueType, MutableMapping[str, Any]]:
        if self._connector_state_converter.is_state_message_compatible(state):
            partitioned_state = self._connector_state_converter.deserialize(state)
            slices_from_partitioned_state = partitioned_state.get("slices", [])

            value_from_partitioned_state = None
            if slices_from_partitioned_state:
                # We assume here that the slices have been already merged
                first_slice = slices_from_partitioned_state[0]
                value_from_partitioned_state = (
                    first_slice[self._connector_state_converter.MOST_RECENT_RECORD_KEY]
                    if self._connector_state_converter.MOST_RECENT_RECORD_KEY in first_slice
                    else first_slice[self._connector_state_converter.END_KEY]
                )
            return (
                value_from_partitioned_state
                or self._start
                or self._connector_state_converter.zero_value,
                partitioned_state,
            )
        return self._connector_state_converter.convert_from_sequential_state(
            self._cursor_field, state, self._start
        )

    def observe(self, record: Record) -> None:
        # Because observe writes to the most_recent_cursor_value_per_partition mapping,
        # it is not thread-safe. However, this shouldn't lead to concurrency issues because
        # observe() is only invoked by PartitionReader.process_partition(). Since the map is
        # broken down according to partition, concurrent threads processing only read/write
        # from different keys which avoids any conflicts.
        #
        # If we were to add thread safety, we should implement a lock per-partition
        # which is instantiated during stream_slices()
        most_recent_cursor_value = self._most_recent_cursor_value_per_partition.get(
            record.associated_slice
        )
        try:
            cursor_value = self._extract_cursor_value(record)

            if most_recent_cursor_value is None or most_recent_cursor_value < cursor_value:
                self._most_recent_cursor_value_per_partition[record.associated_slice] = cursor_value
            elif most_recent_cursor_value > cursor_value:
                self._is_ascending_order = False
        except ValueError:
            self._log_for_record_without_cursor_value()

    def _extract_cursor_value(self, record: Record) -> Any:
        return self._connector_state_converter.parse_value(self._cursor_field.extract_value(record))

    def close_partition(self, partition: Partition) -> None:
        with self._lock:
            slice_count_before = len(self._concurrent_state.get("slices", []))
            self._add_slice_to_state(partition)
            if slice_count_before < len(
                self._concurrent_state["slices"]
            ):  # only emit if at least one slice has been processed
                self._merge_partitions()
                self._emit_state_message()
        self._has_closed_at_least_one_slice = True

    def _add_slice_to_state(self, partition: Partition) -> None:
        most_recent_cursor_value = self._most_recent_cursor_value_per_partition.get(
            partition.to_slice()
        )

        if self._slice_boundary_fields:
            if "slices" not in self._concurrent_state:
                raise RuntimeError(
                    f"The state for stream {self._stream_name} should have at least one slice to delineate the sync start time, but no slices are present. This is unexpected. Please contact Support."
                )
            self._concurrent_state["slices"].append(
                {
                    self._connector_state_converter.START_KEY: self._extract_from_slice(
                        partition, self._slice_boundary_fields[self._START_BOUNDARY]
                    ),
                    self._connector_state_converter.END_KEY: self._extract_from_slice(
                        partition, self._slice_boundary_fields[self._END_BOUNDARY]
                    ),
                    self._connector_state_converter.MOST_RECENT_RECORD_KEY: most_recent_cursor_value,
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

            self._concurrent_state["slices"].append(
                {
                    self._connector_state_converter.START_KEY: self.start,
                    self._connector_state_converter.END_KEY: most_recent_cursor_value,
                    self._connector_state_converter.MOST_RECENT_RECORD_KEY: most_recent_cursor_value,
                }
            )

    def _emit_state_message(self) -> None:
        self._connector_state_manager.update_state_for_stream(
            self._stream_name,
            self._stream_namespace,
            self.state,
        )
        state_message = self._connector_state_manager.create_state_message(
            self._stream_name, self._stream_namespace
        )
        self._message_repository.emit_message(state_message)

    def _merge_partitions(self) -> None:
        self._concurrent_state["slices"] = self._connector_state_converter.merge_intervals(
            self._concurrent_state["slices"]
        )

    def _extract_from_slice(self, partition: Partition, key: str) -> CursorValueType:
        try:
            _slice = partition.to_slice()
            if not _slice:
                raise KeyError(f"Could not find key `{key}` in empty slice")
            return self._connector_state_converter.parse_value(_slice[key])  # type: ignore  # we expect the devs to specify a key that would return a CursorValueType
        except KeyError as exception:
            raise KeyError(
                f"Partition is expected to have key `{key}` but could not be found"
            ) from exception

    def ensure_at_least_one_state_emitted(self) -> None:
        """
        The platform expect to have at least one state message on successful syncs. Hence, whatever happens, we expect this method to be
        called.
        """
        self._emit_state_message()

    def stream_slices(self) -> Iterable[StreamSlice]:
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
            yield from self._split_per_slice_range(
                self._start,
                self._concurrent_state["slices"][0][self._connector_state_converter.START_KEY],
                False,
            )

        if len(self._concurrent_state["slices"]) == 1:
            yield from self._split_per_slice_range(
                self._calculate_lower_boundary_of_last_slice(
                    self._concurrent_state["slices"][0][self._connector_state_converter.END_KEY]
                ),
                self._end_provider(),
                True,
            )
        elif len(self._concurrent_state["slices"]) > 1:
            for i in range(len(self._concurrent_state["slices"]) - 1):
                if self._cursor_granularity:
                    yield from self._split_per_slice_range(
                        self._concurrent_state["slices"][i][self._connector_state_converter.END_KEY]
                        + self._cursor_granularity,
                        self._concurrent_state["slices"][i + 1][
                            self._connector_state_converter.START_KEY
                        ],
                        False,
                    )
                else:
                    yield from self._split_per_slice_range(
                        self._concurrent_state["slices"][i][
                            self._connector_state_converter.END_KEY
                        ],
                        self._concurrent_state["slices"][i + 1][
                            self._connector_state_converter.START_KEY
                        ],
                        False,
                    )
            yield from self._split_per_slice_range(
                self._calculate_lower_boundary_of_last_slice(
                    self._concurrent_state["slices"][-1][self._connector_state_converter.END_KEY]
                ),
                self._end_provider(),
                True,
            )
        else:
            raise ValueError("Expected at least one slice")

    def _is_start_before_first_slice(self) -> bool:
        return (
            self._start is not None
            and self._start
            < self._concurrent_state["slices"][0][self._connector_state_converter.START_KEY]
        )

    def _calculate_lower_boundary_of_last_slice(
        self, lower_boundary: CursorValueType
    ) -> CursorValueType:
        if self._lookback_window:
            return lower_boundary - self._lookback_window
        return lower_boundary

    def _split_per_slice_range(
        self, lower: CursorValueType, upper: CursorValueType, upper_is_end: bool
    ) -> Iterable[StreamSlice]:
        if lower >= upper:
            return

        if self._start and upper < self._start:
            return

        lower = max(lower, self._start) if self._start else lower
        if not self._slice_range or self._evaluate_upper_safely(lower, self._slice_range) >= upper:
            clamped_lower = self._clamping_strategy.clamp(lower)
            clamped_upper = self._clamping_strategy.clamp(upper)
            start_value, end_value = (
                (clamped_lower, clamped_upper - self._cursor_granularity)
                if self._cursor_granularity and not upper_is_end
                else (clamped_lower, clamped_upper)
            )
            yield StreamSlice(
                partition={},
                cursor_slice={
                    self._slice_boundary_fields_wrapper[
                        self._START_BOUNDARY
                    ]: self._connector_state_converter.output_format(start_value),
                    self._slice_boundary_fields_wrapper[
                        self._END_BOUNDARY
                    ]: self._connector_state_converter.output_format(end_value),
                },
            )
        else:
            stop_processing = False
            current_lower_boundary = lower
            while not stop_processing:
                current_upper_boundary = min(
                    self._evaluate_upper_safely(current_lower_boundary, self._slice_range), upper
                )
                has_reached_upper_boundary = current_upper_boundary >= upper

                clamped_upper = (
                    self._clamping_strategy.clamp(current_upper_boundary)
                    if current_upper_boundary != upper
                    else current_upper_boundary
                )
                clamped_lower = self._clamping_strategy.clamp(current_lower_boundary)
                if clamped_lower >= clamped_upper:
                    # clamping collapsed both values which means that it is time to stop processing
                    # FIXME should this be replace by proper end_provider
                    break
                start_value, end_value = (
                    (clamped_lower, clamped_upper - self._cursor_granularity)
                    if self._cursor_granularity
                    and (not upper_is_end or not has_reached_upper_boundary)
                    else (clamped_lower, clamped_upper)
                )
                yield StreamSlice(
                    partition={},
                    cursor_slice={
                        self._slice_boundary_fields_wrapper[
                            self._START_BOUNDARY
                        ]: self._connector_state_converter.output_format(start_value),
                        self._slice_boundary_fields_wrapper[
                            self._END_BOUNDARY
                        ]: self._connector_state_converter.output_format(end_value),
                    },
                )
                current_lower_boundary = clamped_upper
                if current_upper_boundary >= upper:
                    stop_processing = True

    def _evaluate_upper_safely(self, lower: CursorValueType, step: GapType) -> CursorValueType:
        """
        Given that we set the default step at datetime.timedelta.max, we will generate an OverflowError when evaluating the next start_date
        This method assumes that users would never enter a step that would generate an overflow. Given that would be the case, the code
        would have broken anyway.
        """
        try:
            return lower + step
        except OverflowError:
            return self._end_provider()

    def should_be_synced(self, record: Record) -> bool:
        """
        Determines if a record should be synced based on its cursor value.
        :param record: The record to evaluate

        :return: True if the record's cursor value falls within the sync boundaries
        """
        try:
            record_cursor_value: CursorValueType = self._extract_cursor_value(record)
        except ValueError:
            self._log_for_record_without_cursor_value()
            return True
        return self.start <= record_cursor_value <= self._end_provider()

    def _log_for_record_without_cursor_value(self) -> None:
        if not self._should_be_synced_logger_triggered:
            LOGGER.warning(
                f"Could not find cursor field `{self.cursor_field.cursor_field_key}` in record for stream {self._stream_name}. The incremental sync will assume it needs to be synced"
            )
            self._should_be_synced_logger_triggered = True

    def reduce_slice_range(self, stream_slice: StreamSlice) -> StreamSlice:
        # In theory, we might be more flexible here meaning that it doesn't need to be in ascending order but it just
        # needs to be ordered. For now though, we will only support ascending order.
        if not self._is_ascending_order:
            LOGGER.warning(
                "Attempting to reduce slice while records are not returned in incremental order might lead to missing records"
            )

        if stream_slice in self._most_recent_cursor_value_per_partition:
            return StreamSlice(
                partition=stream_slice.partition,
                cursor_slice={
                    self._slice_boundary_fields_wrapper[
                        self._START_BOUNDARY
                    ]: self._connector_state_converter.output_format(
                        self._most_recent_cursor_value_per_partition[stream_slice]
                    ),
                    self._slice_boundary_fields_wrapper[
                        self._END_BOUNDARY
                    ]: stream_slice.cursor_slice[
                        self._slice_boundary_fields_wrapper[self._END_BOUNDARY]
                    ],
                },
                extra_fields=stream_slice.extra_fields,
            )
        else:
            return stream_slice
