# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping
from typing import Any, cast

from pandas import DataFrame
from typing_extensions import Self


class DatasetBase(ABC, Iterator[Mapping[str, Any]]):
    """Base implementation for all datasets."""

    def __iter__(self) -> Self:
        """Return the iterator object (usually self)."""
        return self

    @abstractmethod
    def __next__(self) -> Mapping[str, Any]:
        """Return the next value from the iterator."""
        raise NotImplementedError

    def to_pandas(self) -> DataFrame:
        """Return a pandas DataFrame representation of the dataset."""
        # Technically, we return an iterator of Mapping objects. However, pandas
        # expects an iterator of dict objects. This cast is safe because we know
        # duck typing is correct for this use case.
        return DataFrame(cast(Iterator[dict[str, Any]], self))
