#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, AirbyteStateType, AirbyteStream, AirbyteStreamState, StreamDescriptor
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record


class DefaultConcurrentFileBasedCursor(DefaultFileBasedCursor, Cursor):
    def __init__(
        self,
        stream: AirbyteStream,
        stream_config: FileBasedStreamConfig,
        message_repository: MessageRepository,
    ) -> None:
        self.stream = stream
        self._most_recent_record = None
        self._message_repository = message_repository
        DefaultFileBasedCursor.__init__(self, stream_config)

    def observe(self, record: Record) -> None:
        pass  # TODO: do we need this to do something?

    def close_partition(self, partition: Partition) -> None:
        state_message = AirbyteMessage(
            type=MessageType.STATE,
            state=AirbyteStateMessage(
                type=AirbyteStateType.STREAM,
                stream=AirbyteStreamState(stream_descriptor=StreamDescriptor(name=self.stream.name), stream_state=self.get_state()),
                data={self.stream.name: self.get_state()},
            ),
        )
        self._emit_message(state_message)

    def _emit_message(self, message: AirbyteMessage) -> None:
        self._message_repository.emit_message(message)
