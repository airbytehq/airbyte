from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Mapping, Any, Generic, TypeVar, Iterable

from airbyte_protocol.models import ConfiguredAirbyteCatalog
from pydantic import BaseModel, Field

from airbyte_cdk.v2 import State
from .datetime_range_tracker import DatetimeRangeTracker
from airbyte_cdk.v2.concurrency import PartitionDescriptor, PartitionGenerator

StateType = TypeVar('StateType', bound=State)
PartitionType = TypeVar('PartitionType', bound=PartitionDescriptor)


class StateManager(ABC, Generic[StateType, PartitionType]):
    def observe(self, record: Mapping[str, Any]) -> Optional[StateType]:
        """ If the state was updated as a result of observing this record, returns a state object"""
        pass

    @abstractmethod
    def notify_partition_complete(self, partition_descriptor: PartitionType) -> StateType:
        """ Called when a partition has successfully synced"""

    @abstractmethod
    def get_state(self) -> StateType:
        """Returns the current checkpointable state. """

    @staticmethod
    @abstractmethod
    def from_state(state: StateType = None):
        """Return a new instance of the state manager initialized with the state object"""


class DatetimeState(State, BaseModel):
    copied_ranges: List[Tuple[datetime, datetime]] = Field(...)

    @staticmethod
    def from_dict(d: Mapping[str, Any]) -> StateType:
        return DatetimeState.parse_obj(d)

    def to_dict(self) -> Mapping[str, Any]:
        return self.dict(exclude_unset=True)


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
        for uncopied_range in range_tracker.get_uncopied_ranges(self.start, self.end, self.preferred_partition_size):
            part_start = uncopied_range[0]
            part_end = uncopied_range[1]
            yield DatetimePartitionDescriptor(f"{part_start} -- {part_end}", {}, part_start, part_end)


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
