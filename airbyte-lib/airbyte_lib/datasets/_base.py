from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

from pandas import DataFrame


class DatasetBase(ABC):
    """Base implementation for all datasets."""

    @abstractmethod
    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Return an iterator of records in the dataset."""
        ...

    def to_pandas(self) -> DataFrame:
        """Return a pandas DataFrame representation of the dataset."""
        return DataFrame(iter(self))
