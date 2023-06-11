from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional, Mapping, Any, Generic, TypeVar

from pydantic import BaseModel, Field

from airbyte_cdk.v2.state import State, DatetimeRangeTracker
from airbyte_cdk.v2.concurrency.partitioned_stream import PartitionDescriptor

# TODO fix the generics. The class itself should be generic, not just the method parameters
StateType = TypeVar('StateType', bound=State)
PartitionType = TypeVar('PartitionType', bound=PartitionDescriptor)


class StateManager(ABC, Generic[StateType, PartitionType]):
    def observe(self, record: Mapping[str, Any]) -> Optional[StateType]:
        """ If the state was updated as a result of observing this record, returns a state object"""
        pass

    @abstractmethod
    def notify_partition_complete(self, partition_descriptor: PartitionType):
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


class DatetimeStateManager(StateManager[DatetimeState, DatetimePartitionDescriptor]):
    def __init__(self, state: DatetimeState):
        self.daterange_tracker = DatetimeRangeTracker(copied_ranges=state.copied_ranges)

    @staticmethod
    def from_state(state: DatetimeState = None):
        return DatetimeStateManager(state)

    def notify_partition_complete(self, partition_descriptor: DatetimePartitionDescriptor):
        # TODO
        raise Exception()

    def get_state(self) -> DatetimeState:
        # TODO
        raise Exception()
