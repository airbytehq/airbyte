#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping

from airbyte_cdk.sources.streams.record import Record


class Partition(ABC):
    @abstractmethod
    def read(self) -> Iterable[Record]:
        pass

    @abstractmethod
    def to_slice(self) -> Mapping[str, Any]:
        pass
