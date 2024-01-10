# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from collections.abc import Callable, Iterator
from typing import Any

from pandas import DataFrame

from airbyte_lib.datasets import DatasetBase


class LazyDataset(DatasetBase):
    def __init__(
        self, on_iter: Callable, on_open: Callable | None, on_close: Callable | None
    ) -> None:
        self._on_iter = on_iter
        self._on_open = on_open
        self._on_close = on_close

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return self._on_iter()

    def to_pandas(self) -> DataFrame:
        raise NotImplementedError
