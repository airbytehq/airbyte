#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterable, List, MutableMapping

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.concurrent.cursor.abstract_concurrent_file_based_cursor import AbstractConcurrentFileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamState
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record

if TYPE_CHECKING:
    from airbyte_cdk.sources.file_based.stream.concurrent.adapters import FileBasedStreamPartition


class FileBasedNoopCursor(AbstractConcurrentFileBasedCursor):
    def __init__(self, stream_config: FileBasedStreamConfig, **kwargs: Any):
        pass

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {}

    def observe(self, record: Record) -> None:
        pass

    def close_partition(self, partition: Partition) -> None:
        pass

    def set_pending_partitions(self, partitions: List["FileBasedStreamPartition"]) -> None:
        pass

    def add_file(self, file: RemoteFile) -> None:
        pass

    def get_files_to_sync(self, all_files: Iterable[RemoteFile], logger: logging.Logger) -> Iterable[RemoteFile]:
        return all_files

    def get_state(self) -> MutableMapping[str, Any]:
        return {}

    def set_initial_state(self, value: StreamState) -> None:
        return None

    def get_start_time(self) -> datetime:
        return datetime.min

    def emit_state_message(self) -> None:
        pass

    def ensure_at_least_one_state_emitted(self) -> None:
        pass
