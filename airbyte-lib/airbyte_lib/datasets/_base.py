from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

from pandas import DataFrame


class DatasetBase(ABC):
    @abstractmethod
    def __iter__(self) -> Iterator[dict[str, Any]]:
        ...

    @abstractmethod
    def to_pandas(self) -> DataFrame:
        ...
