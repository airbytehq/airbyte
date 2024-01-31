#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from abc import abstractmethod
from datetime import datetime
from typing import Any, Iterable, MutableMapping

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.cursor import AbstractFileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamState
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record


class AbstractFileBasedConcurrentCursor(Cursor, AbstractFileBasedCursor):
    @property
    @abstractmethod
    def state(self) -> MutableMapping[str, Any]:
        ...

    @abstractmethod
    def add_file(self, file: RemoteFile) -> None:
        ...

    @abstractmethod
    def set_initial_state(self, value: StreamState) -> None:
        ...

    @abstractmethod
    def get_state(self) -> MutableMapping[str, Any]:
        ...

    @abstractmethod
    def get_start_time(self) -> datetime:
        ...

    @abstractmethod
    def get_files_to_sync(self, all_files: Iterable[RemoteFile], logger: logging.Logger) -> Iterable[RemoteFile]:
        ...

    @abstractmethod
    def observe(self, record: Record) -> None:
        ...

    @abstractmethod
    def close_partition(self, partition: Partition) -> None:
        ...

    @abstractmethod
    def set_pending_partitions(self, partitions: Iterable[Partition]) -> None:
        ...


class FileBasedNoopCursor(AbstractFileBasedConcurrentCursor):
    def __init__(self, stream_config: FileBasedStreamConfig, **kwargs: Any):
        pass

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {}

    def add_file(self, file: RemoteFile) -> None:
        return None

    def set_initial_state(self, value: StreamState) -> None:
        return None

    def get_state(self) -> MutableMapping[str, Any]:
        return {}

    def get_start_time(self) -> datetime:
        return datetime.min

    def get_files_to_sync(self, all_files: Iterable[RemoteFile], logger: logging.Logger) -> Iterable[RemoteFile]:
        return []

    def observe(self, record: Record) -> None:
        return None

    def close_partition(self, partition: Partition) -> None:
        return None

    def ensure_at_least_one_state_emitted(self) -> None:
        return None

    def set_pending_partitions(self, partitions: Iterable[Partition]) -> None:
        return None
