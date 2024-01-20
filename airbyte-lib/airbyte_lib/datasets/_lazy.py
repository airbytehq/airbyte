# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from overrides import overrides
from typing_extensions import Self

from airbyte_lib.datasets import DatasetBase


if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


class LazyDataset(DatasetBase):
    """A dataset that is loaded incrementally from a source or a SQL query.

    TODO: Test and debug this. It is not yet implemented anywhere in the codebase.
          For now it servers as a placeholder.
    """

    def __init__(
        self,
        iterator: Iterator,
        on_open: Callable | None = None,
        on_close: Callable | None = None,
    ) -> None:
        self._iterator = iterator
        self._on_open = on_open
        self._on_close = on_close
        raise NotImplementedError("This class is not implemented yet.")

    @overrides
    def __iter__(self) -> Self:
        raise NotImplementedError("This class is not implemented yet.")
        # Pseudocode:
        # if self._on_open is not None:
        #     self._on_open()

        # yield from self._iterator

        # if self._on_close is not None:
        #     self._on_close()

    def __next__(self) -> dict[str, Any]:
        return next(self._iterator)
