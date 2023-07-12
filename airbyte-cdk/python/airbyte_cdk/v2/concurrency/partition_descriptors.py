from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Mapping, Any, Generic, Iterable

from airbyte_protocol.models import ConfiguredAirbyteCatalog

from airbyte_cdk.v2 import StateType

PartitionType = TypeVar('PartitionType', bound='PartitionDescriptor')


@dataclass
class PartitionDescriptor:
    """
        TODO: A partition could be described by more than one thing e.g: date range and a configuration setting, for example:
            sync_deleted_records(bool) or lookback_window
            those are two examples of configurations which, if changed, the existing stream state is no longer correct, and the stream
            needs to be recomputed.
            Should we try to solve this as part of partition descriptors?
            Alternatively we could just not bother with this.
    """
    partition_id: str
    metadata: Mapping[str, Any]


class PartitionGenerator(ABC, Generic[PartitionType, StateType]):
    @abstractmethod
    def generate_partitions(self, state: StateType, catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any]) -> Iterable[
            PartitionType]:
        """ Generates partitions """



