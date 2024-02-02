# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping
from typing import Any, cast

from pandas import DataFrame


class DatasetBase(ABC):
    """Base implementation for all datasets."""

    def __init__(self) -> None:
        self.__length: int | None = None

    @abstractmethod
    def __iter__(self) -> Iterator[Mapping[str, Any]]:
        """Return the iterator of records."""
        raise NotImplementedError

    def __len__(self) -> int:
        """Return the number of records in the dataset.

        This method caches the length of the dataset after the first call.
        """
        if self.__length is None:
            self.__length = sum(1 for _ in self)

        return self.__length

    def to_pandas(self) -> DataFrame:
        """Return a pandas DataFrame representation of the dataset.

        The base implementation simply passes the record iterator to Panda's DataFrame constructor.
        """
        # Technically, we return an iterator of Mapping objects. However, pandas
        # expects an iterator of dict objects. This cast is safe because we know
        # duck typing is correct for this use case.
        return DataFrame(cast(Iterator[dict[str, Any]], self))
