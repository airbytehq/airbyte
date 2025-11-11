#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import logging
import threading
import time
from collections import OrderedDict
from copy import deepcopy
from datetime import timedelta
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, TypeVar

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    StreamDescriptor,
)
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.checkpoint.per_partition_key_serializer import (
    PerPartitionKeySerializer,
)
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor, Cursor, CursorField
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import (
    AbstractStreamStateConverter,
)
from airbyte_cdk.sources.types import Record, StreamSlice, StreamState

logger = logging.getLogger("airbyte")


T = TypeVar("T")


def iterate_with_last_flag_and_state(
    generator: Iterable[T], get_stream_state_func: Callable[[], Optional[Mapping[str, StreamState]]]
) -> Iterable[tuple[T, bool, Any]]:
    """
    Iterates over the given generator, yielding tuples containing the element, a flag
    indicating whether it's the last element in the generator, and the result of
    `get_stream_state_func` applied to the element.

    Args:
        generator: The iterable to iterate over.
        get_stream_state_func: A function that takes an element from the generator and
            returns its state.

    Returns:
        An iterator that yields tuples of the form (element, is_last, state).
    """

    iterator = iter(generator)

    try:
        current = next(iterator)
        state = get_stream_state_func()
    except StopIteration:
        return  # Return an empty iterator

    for next_item in iterator:
        yield current, False, state
        current = next_item
        state = get_stream_state_func()

    yield current, True, state


class Timer:
    """
    A simple timer class that measures elapsed time in seconds using a high-resolution performance counter.
    """

    def __init__(self) -> None:
        self._start: Optional[int] = None

    def start(self) -> None:
        self._start = time.perf_counter_ns()

    def finish(self) -> int:
        if self._start:
            return ((time.perf_counter_ns() - self._start) / 1e9).__ceil__()
        else:
            raise RuntimeError("Global substream cursor timer not started")

    def is_running(self) -> bool:
        return self._start is not None


class ConcurrentCursorFactory:
    def __init__(self, create_function: Callable[..., ConcurrentCursor]):
        self._create_function = create_function

    def create(
        self, stream_state: Mapping[str, Any], runtime_lookback_window: Optional[timedelta]
    ) -> ConcurrentCursor:
        return self._create_function(
            stream_state=stream_state, runtime_lookback_window=runtime_lookback_window
        )


class ConcurrentPerPartitionCursor(Cursor):
    """
    Manages state per partition when a stream has many partitions, preventing data loss or duplication.

    Attributes:
        DEFAULT_MAX_PARTITIONS_NUMBER (int): Maximum number of partitions to retain in memory (default is 10,000). This limit needs to be higher than the number of threads we might enqueue (which is represented by ThreadPoolManager.DEFAULT_MAX_QUEUE_SIZE). If not, we could have partitions that have been generated and submitted to the ThreadPool but got deleted from the ConcurrentPerPartitionCursor and when closing them, it will generate KeyError.

    - **Partition Limitation Logic**
      Ensures the number of tracked partitions does not exceed the specified limit to prevent memory overuse. Oldest partitions are removed when the limit is reached.

    - **Global Cursor Fallback**
      New partitions use global state as the initial state to progress the state for deleted or new partitions. The history data added after the initial sync will be missing.

    CurrentPerPartitionCursor expects the state of the ConcurrentCursor to follow the format {cursor_field: cursor_value}.
    """

    DEFAULT_MAX_PARTITIONS_NUMBER = 25_000
    SWITCH_TO_GLOBAL_LIMIT = 10_000
    _NO_STATE: Mapping[str, Any] = {}
    _NO_CURSOR_STATE: Mapping[str, Any] = {}
    _GLOBAL_STATE_KEY = "state"
    _PERPARTITION_STATE_KEY = "states"
    _IS_PARTITION_DUPLICATION_LOGGED = False
    _PARENT_STATE = 0
    _GENERATION_SEQUENCE = 1

    def __init__(
        self,
        cursor_factory: ConcurrentCursorFactory,
        partition_router: PartitionRouter,
        stream_name: str,
        stream_namespace: Optional[str],
        stream_state: Any,
        message_repository: MessageRepository,
        connector_state_manager: ConnectorStateManager,
        connector_state_converter: AbstractStreamStateConverter,
        cursor_field: CursorField,
        use_global_cursor: bool = False,
        attempt_to_create_cursor_if_not_provided: bool = False,
    ) -> None:
        self._global_cursor: Optional[StreamState] = {}
        self._stream_name = stream_name
        self._stream_namespace = stream_namespace
        self._message_repository = message_repository
        self._connector_state_manager = connector_state_manager
        self._connector_state_converter = connector_state_converter
        self._cursor_field = cursor_field

        self._cursor_factory = cursor_factory  # self._cursor_factory is flagged as private but is used in model_to_component_factory to ease pagination reset instantiation
        self._partition_router = partition_router

        # The dict is ordered to ensure that once the maximum number of partitions is reached,
        # the oldest partitions can be efficiently removed, maintaining the most recent partitions.
        self._cursor_per_partition: OrderedDict[str, ConcurrentCursor] = OrderedDict()
        self._semaphore_per_partition: OrderedDict[str, threading.Semaphore] = OrderedDict()

        # Parent-state tracking: store each partition’s parent state in creation order
        self._partition_parent_state_map: OrderedDict[str, tuple[Mapping[str, Any], int]] = (
            OrderedDict()
        )
        self._parent_state: Optional[StreamState] = None

        # Tracks when the last slice for partition is emitted
        self._partitions_done_generating_stream_slices: set[str] = set()
        # Used to track the index of partitions that are not closed yet
        self._processing_partitions_indexes: List[int] = list()
        self._generated_partitions_count: int = 0
        # Dictionary to map partition keys to their index
        self._partition_key_to_index: dict[str, int] = {}

        self._lock = threading.Lock()
        self._lookback_window: int = 0
        self._new_global_cursor: Optional[StreamState] = None
        self._number_of_partitions: int = 0
        self._use_global_cursor: bool = use_global_cursor
        self._partition_serializer = PerPartitionKeySerializer()

        # Track the last time a state message was emitted
        self._last_emission_time: float = 0.0
        self._timer = Timer()

        self._set_initial_state(stream_state)

        # FIXME this is a temporary field the time of the migration from declarative cursors to concurrent ones
        self._attempt_to_create_cursor_if_not_provided = attempt_to_create_cursor_if_not_provided
        self._synced_some_data = False
        self._logged_regarding_datetime_format_error = False

    @property
    def cursor_field(self) -> CursorField:
        return self._cursor_field

    @property
    def state(self) -> MutableMapping[str, Any]:
        state: dict[str, Any] = {"use_global_cursor": self._use_global_cursor}
        if not self._use_global_cursor:
            states = []
            for partition_tuple, cursor in self._cursor_per_partition.items():
                if cursor.state:
                    states.append(
                        {
                            "partition": self._to_dict(partition_tuple),
                            "cursor": copy.deepcopy(cursor.state),
                        }
                    )
            state[self._PERPARTITION_STATE_KEY] = states

        if self._global_cursor:
            state[self._GLOBAL_STATE_KEY] = self._global_cursor
        if self._lookback_window is not None:
            state["lookback_window"] = self._lookback_window
        if self._parent_state is not None:
            state["parent_state"] = self._parent_state
        return state

    def close_partition(self, partition: Partition) -> None:
        # Attempt to retrieve the stream slice
        stream_slice: Optional[StreamSlice] = partition.to_slice()  # type: ignore[assignment]

        # Ensure stream_slice is not None
        if stream_slice is None:
            raise ValueError("stream_slice cannot be None")

        partition_key = self._to_partition_key(stream_slice.partition)
        with self._lock:
            self._semaphore_per_partition[partition_key].acquire()
            if not self._use_global_cursor:
                cursor = self._cursor_per_partition[partition_key]
                cursor.close_partition(partition=partition)
                if (
                    partition_key in self._partitions_done_generating_stream_slices
                    and self._semaphore_per_partition[partition_key]._value == 0
                ):
                    self._update_global_cursor(cursor.state[self.cursor_field.cursor_field_key])

            # Clean up the partition if it is fully processed
            self._cleanup_if_done(partition_key)

            self._check_and_update_parent_state()

            self._emit_state_message()

    def _check_and_update_parent_state(self) -> None:
        last_closed_state = None

        while self._partition_parent_state_map:
            earliest_key, (candidate_state, candidate_seq) = next(
                iter(self._partition_parent_state_map.items())
            )

            # if any partition that started <= candidate_seq is still open, we must wait
            if (
                self._processing_partitions_indexes
                and self._processing_partitions_indexes[0] <= candidate_seq
            ):
                break

            # safe to pop
            self._partition_parent_state_map.popitem(last=False)
            last_closed_state = candidate_state

        if last_closed_state is not None:
            self._parent_state = last_closed_state

    def ensure_at_least_one_state_emitted(self) -> None:
        """
        The platform expects at least one state message on successful syncs. Hence, whatever happens, we expect this method to be
        called.
        """
        if not any(
            semaphore_item[1]._value for semaphore_item in self._semaphore_per_partition.items()
        ):
            if self._synced_some_data:
                # we only update those if we actually synced some data
                self._global_cursor = self._new_global_cursor
                self._lookback_window = self._timer.finish()
            self._parent_state = self._partition_router.get_stream_state()
        self._emit_state_message(throttle=False)

    def _throttle_state_message(self) -> Optional[float]:
        """
        Throttles the state message emission to once every 600 seconds.
        """
        current_time = time.time()
        if current_time - self._last_emission_time <= 600:
            return None
        return current_time

    def _emit_state_message(self, throttle: bool = True) -> None:
        if throttle:
            current_time = self._throttle_state_message()
            if current_time is None:
                return
            self._last_emission_time = current_time
            # Skip state emit for global cursor if parent state is empty
            if self._use_global_cursor and not self._parent_state:
                return

        self._connector_state_manager.update_state_for_stream(
            self._stream_name,
            self._stream_namespace,
            self.state,
        )
        state_message = self._connector_state_manager.create_state_message(
            self._stream_name, self._stream_namespace
        )
        self._message_repository.emit_message(state_message)

    def stream_slices(self) -> Iterable[StreamSlice]:
        if self._timer.is_running():
            raise RuntimeError("stream_slices has been executed more than once.")

        slices = self._partition_router.stream_slices()
        self._timer.start()
        for partition, last, parent_state in iterate_with_last_flag_and_state(
            slices, self._partition_router.get_stream_state
        ):
            yield from self._generate_slices_from_partition(partition, parent_state)

    def _generate_slices_from_partition(
        self, partition: StreamSlice, parent_state: Mapping[str, Any]
    ) -> Iterable[StreamSlice]:
        # Ensure the maximum number of partitions is not exceeded
        self._ensure_partition_limit()

        partition_key = self._to_partition_key(partition.partition)

        cursor = self._cursor_per_partition.get(self._to_partition_key(partition.partition))
        if not cursor:
            cursor = self._create_cursor(
                self._global_cursor,
                self._lookback_window if self._global_cursor else 0,
            )
            with self._lock:
                self._number_of_partitions += 1
                self._cursor_per_partition[partition_key] = cursor

        if partition_key in self._semaphore_per_partition:
            if not self._IS_PARTITION_DUPLICATION_LOGGED:
                logger.warning(f"Partition duplication detected for stream {self._stream_name}")
                self._IS_PARTITION_DUPLICATION_LOGGED = True
            return
        else:
            self._semaphore_per_partition[partition_key] = threading.Semaphore(0)

        with self._lock:
            seq = self._generated_partitions_count
            self._generated_partitions_count += 1
            self._processing_partitions_indexes.append(seq)
            self._partition_key_to_index[partition_key] = seq

            if (
                len(self._partition_parent_state_map) == 0
                or self._partition_parent_state_map[
                    next(reversed(self._partition_parent_state_map))
                ][self._PARENT_STATE]
                != parent_state
            ):
                self._partition_parent_state_map[partition_key] = (deepcopy(parent_state), seq)

        for cursor_slice, is_last_slice, _ in iterate_with_last_flag_and_state(
            cursor.stream_slices(),
            lambda: None,
        ):
            self._semaphore_per_partition[partition_key].release()
            if is_last_slice:
                self._partitions_done_generating_stream_slices.add(partition_key)
            yield StreamSlice(
                partition=partition, cursor_slice=cursor_slice, extra_fields=partition.extra_fields
            )

    def _ensure_partition_limit(self) -> None:
        """
        Ensure the maximum number of partitions does not exceed the predefined limit.

        Steps:
        1. Attempt to remove partitions that are marked as finished in `_finished_partitions`.
           These partitions are considered processed and safe to delete.
        2. If the limit is still exceeded and no finished partitions are available for removal,
           remove the oldest partition unconditionally. We expect failed partitions to be removed.

        Logging:
        - Logs a warning each time a partition is removed, indicating whether it was finished
          or removed due to being the oldest.
        """
        if not self._use_global_cursor and self.limit_reached():
            logger.info(
                f"Exceeded the 'SWITCH_TO_GLOBAL_LIMIT' of {self.SWITCH_TO_GLOBAL_LIMIT}. "
                f"Switching to global cursor for {self._stream_name}."
            )
            self._use_global_cursor = True

        with self._lock:
            while len(self._cursor_per_partition) > self.DEFAULT_MAX_PARTITIONS_NUMBER - 1:
                # Try removing finished partitions first
                for partition_key in list(self._cursor_per_partition.keys()):
                    if partition_key not in self._partition_key_to_index:
                        oldest_partition = self._cursor_per_partition.pop(
                            partition_key
                        )  # Remove the oldest partition
                        logger.debug(
                            f"The maximum number of partitions has been reached. Dropping the oldest finished partition: {oldest_partition}. Over limit: {self._number_of_partitions - self.DEFAULT_MAX_PARTITIONS_NUMBER}."
                        )
                        break
                else:
                    # If no finished partitions can be removed, fall back to removing the oldest partition
                    oldest_partition = self._cursor_per_partition.popitem(last=False)[
                        1
                    ]  # Remove the oldest partition
                    logger.warning(
                        f"The maximum number of partitions has been reached. Dropping the oldest partition: {oldest_partition}. Over limit: {self._number_of_partitions - self.DEFAULT_MAX_PARTITIONS_NUMBER}."
                    )

    def _set_initial_state(self, stream_state: StreamState) -> None:
        """
        Initialize the cursor's state using the provided `stream_state`.

        This method supports global and per-partition state initialization.

        - **Global State**: If `states` is missing, the `state` is treated as global and applied to all partitions.
          The `global state` holds a single cursor position representing the latest processed record across all partitions.

        - **Lookback Window**: Configured via `lookback_window`, it defines the period (in seconds) for reprocessing records.
          This ensures robustness in case of upstream data delays or reordering. If not specified, it defaults to 0.

        - **Per-Partition State**: If `states` is present, each partition's cursor state is initialized separately.

        - **Parent State**: (if available) Used to initialize partition routers based on parent streams.

        Args:
            stream_state (StreamState): The state of the streams to be set. The format of the stream state should be:
                {
                    "states": [
                        {
                            "partition": {
                                "partition_key": "value"
                            },
                            "cursor": {
                                "last_updated": "2023-05-27T00:00:00Z"
                            }
                        }
                    ],
                    "state": {
                        "last_updated": "2023-05-27T00:00:00Z"
                    },
                    lookback_window: 10,
                    "parent_state": {
                        "parent_stream_name": {
                            "last_updated": "2023-05-27T00:00:00Z"
                        }
                    }
                }
        """
        if not stream_state:
            return

        if (
            self._PERPARTITION_STATE_KEY not in stream_state
            and self._GLOBAL_STATE_KEY not in stream_state
        ):
            # We assume that `stream_state` is in a global format that can be applied to all partitions.
            # Example: {"global_state_format_key": "global_state_format_value"}
            self._set_global_state(stream_state)

        else:
            self._use_global_cursor = stream_state.get("use_global_cursor", False)

            self._lookback_window = int(stream_state.get("lookback_window", 0))

            for state in stream_state.get(self._PERPARTITION_STATE_KEY, []):
                self._number_of_partitions += 1
                self._cursor_per_partition[self._to_partition_key(state["partition"])] = (
                    self._create_cursor(state["cursor"])
                )

            # set default state for missing partitions if it is per partition with fallback to global
            if self._GLOBAL_STATE_KEY in stream_state:
                self._set_global_state(stream_state[self._GLOBAL_STATE_KEY])

        # Set initial parent state
        if stream_state.get("parent_state"):
            self._parent_state = stream_state["parent_state"]

    def _set_global_state(self, stream_state: Mapping[str, Any]) -> None:
        """
        Initializes the global cursor state from the provided stream state.

        If the cursor field key is present in the stream state, its value is parsed,
        formatted, and stored as the global cursor. This ensures consistency in state
        representation across partitions.
        """
        if self.cursor_field.cursor_field_key in stream_state:
            global_state_value = stream_state[self.cursor_field.cursor_field_key]
            final_format_global_state_value = self._connector_state_converter.output_format(
                self._connector_state_converter.parse_value(global_state_value)
            )

            fixed_global_state = {
                self.cursor_field.cursor_field_key: final_format_global_state_value
            }

            self._global_cursor = deepcopy(fixed_global_state)
            self._new_global_cursor = deepcopy(fixed_global_state)

    def observe(self, record: Record) -> None:
        if not record.associated_slice:
            raise ValueError(
                "Invalid state as stream slices that are emitted should refer to an existing cursor"
            )

        # if the current record has no cursor value, we cannot meaningfully update the state based on it, so there is nothing more to do
        try:
            record_cursor_value = self._cursor_field.extract_value(record)
        except ValueError:
            return

        try:
            record_cursor = self._connector_state_converter.output_format(
                self._connector_state_converter.parse_value(record_cursor_value)
            )
        except ValueError as exception:
            if not self._logged_regarding_datetime_format_error:
                logger.warning(
                    "Skipping cursor update for stream '%s': failed to parse cursor field '%s' value %r: %s",
                    self._stream_name,
                    self._cursor_field.cursor_field_key,
                    record_cursor_value,
                    exception,
                )
                self._logged_regarding_datetime_format_error = True
            return

        self._synced_some_data = True
        self._update_global_cursor(record_cursor)
        if not self._use_global_cursor:
            self._cursor_per_partition[
                self._to_partition_key(record.associated_slice.partition)
            ].observe(record)

    def _update_global_cursor(self, value: Any) -> None:
        if (
            self._new_global_cursor is None
            or self._new_global_cursor[self.cursor_field.cursor_field_key] < value
        ):
            self._new_global_cursor = {self.cursor_field.cursor_field_key: copy.deepcopy(value)}

    def _cleanup_if_done(self, partition_key: str) -> None:
        """
        Free every in-memory structure that belonged to a completed partition:
        cursor, semaphore, flag inside `_finished_partitions`
        """
        if not (
            partition_key in self._partitions_done_generating_stream_slices
            and self._semaphore_per_partition[partition_key]._value == 0
        ):
            return

        self._semaphore_per_partition.pop(partition_key, None)
        self._partitions_done_generating_stream_slices.discard(partition_key)

        seq = self._partition_key_to_index.pop(partition_key)
        self._processing_partitions_indexes.remove(seq)

        logger.debug(f"Partition {partition_key} fully processed and cleaned up.")

    def _to_partition_key(self, partition: Mapping[str, Any]) -> str:
        return self._partition_serializer.to_partition_key(partition)

    def _to_dict(self, partition_key: str) -> Mapping[str, Any]:
        return self._partition_serializer.to_partition(partition_key)

    def _create_cursor(
        self, cursor_state: Any, runtime_lookback_window: int = 0
    ) -> ConcurrentCursor:
        cursor = self._cursor_factory.create(
            stream_state=deepcopy(cursor_state),
            runtime_lookback_window=timedelta(seconds=runtime_lookback_window),
        )
        return cursor

    def should_be_synced(self, record: Record) -> bool:
        return self._get_cursor(record).should_be_synced(record)

    def _get_cursor(self, record: Record) -> ConcurrentCursor:
        if not record.associated_slice:
            raise ValueError(
                "Invalid state as stream slices that are emitted should refer to an existing cursor"
            )

        if self._use_global_cursor:
            return self._create_cursor(
                self._global_cursor,
                self._lookback_window if self._global_cursor else 0,
            )

        partition_key = self._to_partition_key(record.associated_slice.partition)
        if (
            partition_key not in self._cursor_per_partition
            and not self._attempt_to_create_cursor_if_not_provided
        ):
            raise ValueError(
                "Invalid state as stream slices that are emitted should refer to an existing cursor"
            )
        elif partition_key not in self._cursor_per_partition:
            return self._create_cursor(
                self._global_cursor,
                self._lookback_window if self._global_cursor else 0,
            )
        else:
            return self._cursor_per_partition[partition_key]

    def limit_reached(self) -> bool:
        return self._number_of_partitions > self.SWITCH_TO_GLOBAL_LIMIT

    @staticmethod
    def get_parent_state(
        stream_state: Optional[StreamState], parent_stream_name: str
    ) -> Optional[AirbyteStateMessage]:
        if not stream_state:
            return None

        if "parent_state" not in stream_state:
            logger.warning(
                f"Trying to get_parent_state for stream `{parent_stream_name}` when there are not parent state in the state"
            )
            return None
        elif parent_stream_name not in stream_state["parent_state"]:
            logger.info(
                f"Could not find parent state for stream `{parent_stream_name}`. On parents available are {list(stream_state['parent_state'].keys())}"
            )
            return None

        return AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(parent_stream_name, None),
                stream_state=AirbyteStateBlob(stream_state["parent_state"][parent_stream_name]),
            ),
        )

    @staticmethod
    def get_global_state(
        stream_state: Optional[StreamState], parent_stream_name: str
    ) -> Optional[AirbyteStateMessage]:
        return (
            AirbyteStateMessage(
                type=AirbyteStateType.STREAM,
                stream=AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(parent_stream_name, None),
                    stream_state=AirbyteStateBlob(stream_state["state"]),
                ),
            )
            if stream_state and "state" in stream_state
            else None
        )
