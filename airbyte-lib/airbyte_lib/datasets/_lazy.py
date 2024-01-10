# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from collections.abc import Callable, Iterator
from typing import Any

from overrides import overrides

from airbyte_lib.datasets import DatasetBase


class LazyDataset(DatasetBase):
    """A dataset that is loaded incrementally from a source or a SQL query."""

    def __init__(
        self,
        iterator: Iterator,
        on_open: Callable | None = None,
        on_close: Callable | None = None,
    ) -> None:
        self._iterator = iterator
        self._on_open = on_open
        self._on_close = on_close

    @overrides
    def __iter__(self) -> Iterator[dict[str, Any]]:
        if self._on_open is not None:
            self._on_open()

        yield from self._iterator

        if self._on_close is not None:
            self._on_close()

    def __next__(self) -> dict[str, Any]:
        return next(self._iterator)
