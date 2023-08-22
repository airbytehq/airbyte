#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Generic, Iterable, List, Mapping, Optional, Tuple, TypeVar

from airbyte_protocol.models import ConfiguredAirbyteCatalog
from pydantic import BaseModel, Field

from ..concurrency.partition_descriptors import PartitionDescriptor, PartitionGenerator
from ..state_obj import State
from .datetime_range_tracker import DatetimeRangeTracker

StateType = TypeVar("StateType", bound=State)
PartitionType = TypeVar("PartitionType", bound=PartitionDescriptor)


class StateManager(ABC, Generic[StateType, PartitionType]):
    @abstractmethod
    def observe(self, record: Mapping[str, Any]) -> Optional[StateType]:
        """If the state was updated as a result of observing this record, returns a state object"""

    @abstractmethod
    def notify_partition_complete(self, partition_descriptor: PartitionType) -> StateType:
        """Called when a partition has successfully synced"""

    @abstractmethod
    def get_state(self) -> StateType:
        """Returns the current checkpointable state."""

    @staticmethod
    @abstractmethod
    def from_state(state: StateType = None):
        """Return a new instance of the state manager initialized with the state object"""


class DictState(State):
    def __init__(self, d):
        self._d = d

    @staticmethod
    def from_dict(d: Mapping[str, Any]) -> StateType:
        return DictState(d)

    def to_dict(self) -> Mapping[str, Any]:
        return self._d


class LegacyStateManager(StateManager[StateType, PartitionType]):
    def __init__(self, stream, stream_state, concurrency_stream_group):
        self._stream = stream
        self._partitions = []  # self._stream.generate_partitions(stream_state, concurrency_stream_group)
        self._previous_state = stream_state
        self._latest_record = None

    def observe(self, record: Mapping[str, Any]) -> Optional[StateType]:
        print(f"observe: {record}")
        self._latest_record = record

    def notify_partition_complete(self, partition_descriptor: PartitionType) -> StateType:
        return self.get_state()

    def get_state(self) -> StateType:
        if self._latest_record:
            updated_state = self._stream.get_updated_state(current_stream_state=self._previous_state, latest_record=self._latest_record)
            self._previous_state = updated_state
        return DictState(self._previous_state)

    @staticmethod
    def from_state(state: StateType = None):
        raise ValueError(f"LegacyStateManager does not support state: {state}")


class DatetimeState(State, BaseModel):
    copied_ranges: List[Tuple[datetime, datetime]] = Field(...)

    @staticmethod
    def from_dict(d: Mapping[str, Any]) -> StateType:
        return DatetimeState.parse_obj(d)

    def to_dict(self) -> Mapping[str, Any]:
        return self.dict(exclude_unset=True)


class EmptyState(State):
    @staticmethod
    def from_dict(d: Mapping[str, Any]) -> StateType:
        return EmptyState()

    def to_dict(self) -> Mapping[str, Any]:
        return {}


@dataclass
class DatetimePartitionDescriptor(PartitionDescriptor):
    start_datetime: datetime
    end_datetime: datetime


class DatetimePartitionGenerator(PartitionGenerator[DatetimePartitionDescriptor, DatetimeState]):
    def __init__(self, start: datetime, preferred_partition_size: timedelta = None, end: datetime = None):
        self.start = start
        self.end = end
        self.preferred_partition_size = preferred_partition_size

    def generate_partitions(
        self,
        # state: DatetimeState,
        # catalog: ConfiguredAirbyteCatalog,
        # config: Mapping[str, Any]
    ) -> Iterable[DatetimePartitionDescriptor]:
        range_tracker = DatetimeRangeTracker([])
        # FIXME: this interface is a little problematic. I would prefer if the parition generator generated the partions instead of the range tracker
        # why?
        # because that's more in line with how the partitions are generated in legacy streams (stream_slices())
        # Maybe it would make sense if the DatetimeStateManager accepted the state as input?
        for uncopied_range in range_tracker.get_uncopied_ranges(self.start, self.end, self.preferred_partition_size):
            part_start = uncopied_range[0]
            part_end = uncopied_range[1]
            yield DatetimePartitionDescriptor({}, part_start, part_end)
            # yield DatetimePartitionDescriptor(f"{part_start} -- {part_end}", {}, part_start, part_end)


class DatetimeStateManager(StateManager[DatetimeState, DatetimePartitionDescriptor]):
    def __init__(self, state: DatetimeState = None):
        self.daterange_tracker = DatetimeRangeTracker()

    @staticmethod
    def from_state(state: DatetimeState = None):
        return DatetimeStateManager(state)

    def notify_partition_complete(self, partition_descriptor: DatetimePartitionDescriptor) -> DatetimeState:
        self.daterange_tracker.mark_range_as_copied(partition_descriptor.start_datetime, partition_descriptor.end_datetime)
        return self.get_state()

    def get_state(self) -> DatetimeState:
        return DatetimeState(copied_ranges=self.daterange_tracker.get_copied_ranges())
