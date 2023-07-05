#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Iterable, Mapping, TypeVar

from airbyte_cdk.v2.state_obj import StateType
from airbyte_protocol.models import ConfiguredAirbyteCatalog

PartitionType = TypeVar("PartitionType", bound="PartitionDescriptor")


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

    # partition_id: str
    metadata: Mapping[str, Any]


class PartitionGenerator(ABC, Generic[PartitionType, StateType]):
    @abstractmethod
    def generate_partitions(self, state: StateType) -> Iterable[PartitionType]:
        """Generates partitions"""
