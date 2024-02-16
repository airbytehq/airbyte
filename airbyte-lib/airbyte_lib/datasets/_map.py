# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A generic interface for a set of streams.

TODO: This is a work in progress. It is not yet used by any other code.
TODO: Implement before release, or delete.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from airbyte_lib.datasets._base import DatasetBase


class DatasetMap(Mapping):
    """A generic interface for a set of streams or datasets."""

    def __init__(self) -> None:
        self._datasets: dict[str, DatasetBase] = {}

    def __getitem__(self, key: str) -> DatasetBase:
        return self._datasets[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._datasets)

    def __len__(self) -> int:
        return len(self._datasets)
