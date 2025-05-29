#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterable, List, MutableMapping, Optional

from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.concurrent.cursor.abstract_concurrent_file_based_cursor import AbstractConcurrentFileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamState
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams import NO_CURSOR_STATE_KEY
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record

if TYPE_CHECKING:
    from airbyte_cdk.sources.file_based.stream.concurrent.adapters import FileBasedStreamPartition


class FileBasedFinalStateCursor(AbstractConcurrentFileBasedCursor):
    """Cursor that is used to guarantee at least one state message is emitted for a concurrent file-based stream."""

    def __init__(
        self, stream_config: FileBasedStreamConfig, message_repository: MessageRepository, stream_namespace: Optional[str], **kwargs: Any
    ):
        self._stream_name = stream_config.name
        self._stream_namespace = stream_namespace
        self._message_repository = message_repository
        # Normally the connector state manager operates at the source-level. However, we only need it to write the sentinel
        # state message rather than manage overall source state. This is also only temporary as we move to the resumable
        # full refresh world where every stream uses a FileBasedConcurrentCursor with incremental state.
        self._connector_state_manager = ConnectorStateManager()

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {NO_CURSOR_STATE_KEY: True}

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
        self._connector_state_manager.update_state_for_stream(self._stream_name, self._stream_namespace, self.state)
        state_message = self._connector_state_manager.create_state_message(self._stream_name, self._stream_namespace)
        self._message_repository.emit_message(state_message)
