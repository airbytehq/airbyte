# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from overrides import overrides

from airbyte_cdk.sql.datasets import DatasetBase


if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from airbyte_cdk.models import ConfiguredAirbyteStream


class LazyDataset(DatasetBase):
    """A dataset that is loaded incrementally from a source or a SQL query."""

    def __init__(
        self,
        iterator: Iterator[dict[str, Any]],
        stream_metadata: ConfiguredAirbyteStream,
    ) -> None:
        self._iterator: Iterator[dict[str, Any]] = iterator
        super().__init__(
            stream_metadata=stream_metadata,
        )

    @overrides
    def __iter__(self) -> Iterator[dict[str, Any]]:
        return self._iterator

    def __next__(self) -> Mapping[str, Any]:
        return next(self._iterator)
