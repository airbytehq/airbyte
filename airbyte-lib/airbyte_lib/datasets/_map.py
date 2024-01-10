"""A generic interface for a set of streams."""

from collections.abc import Iterator, Mapping

from airbyte_lib.datasets._base import DatasetBase


class DatasetMap(Mapping):
    def __init__(self) -> None:
        self._streams: dict[str, DatasetBase] = {}

    def __getitem__(self, key: str) -> DatasetBase:
        return self._streams[key]

    def __iter__(self) -> Iterator[DatasetBase]:
        return iter(self._streams)

    def __len__(self) -> int:
        return len(self._streams)
