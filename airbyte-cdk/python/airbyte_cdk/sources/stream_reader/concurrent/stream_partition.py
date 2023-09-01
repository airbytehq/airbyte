#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Mapping


class Partition(ABC):
    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def to_slice(self) -> Mapping[str, Any]:
        pass
