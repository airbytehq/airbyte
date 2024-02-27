# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from overrides import overrides

from airbyte_lib.datasets import DatasetBase


if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping


class LazyDataset(DatasetBase):
    """A dataset that is loaded incrementally from a source or a SQL query."""

    def __init__(
        self,
        iterator: Iterator[Mapping[str, Any]],
    ) -> None:
        self._iterator: Iterator[Mapping[str, Any]] = iterator
        super().__init__()

    @overrides
    def __iter__(self) -> Iterator[Mapping[str, Any]]:
        return self._iterator

    def __next__(self) -> Mapping[str, Any]:
        return next(self._iterator)
