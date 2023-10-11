#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.streams.concurrent.partitions.record import Record


class Partition(ABC):
    """
    A partition is responsible for reading a specific set of data from a source.
    """

    @abstractmethod
    def read(self) -> Iterable[Record]:
        """
        Reads the data from the partition.
        :return: An iterable of records.
        """
        pass

    @abstractmethod
    def to_slice(self) -> Optional[Mapping[str, Any]]:
        """
        Converts the partition to a slice that can be serialized and deserialized.
        :return: A mapping representing a slice
        """
        pass

    @abstractmethod
    def __hash__(self) -> int:
        """
        Returns a hash of the partition.
        Partitions must be hashable so that they can be used as keys in a dictionary.
        """
