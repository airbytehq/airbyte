#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.models import AirbyteStreamStatus
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message


class StreamReader:
    # FIXME: a lot of the code can probably be shared with the PartitionEnqueuer and PartitionReader
    def __init__(self, queue, sentinel, message_repository: MessageRepository) -> None:
        self._queue = queue
        self._sentinel = sentinel
        self._message_repository = message_repository

    def read_from_stream(self, stream: AbstractStream) -> None:
        # print(f"reading from stream: {stream.name}")
        try:
            airbyte_stream = stream.as_airbyte_stream()
            self._message_repository.emit_message(
                stream_status_as_airbyte_message(airbyte_stream.name, airbyte_stream.namespace, AirbyteStreamStatus.STARTED)
            )
            is_first_record = True
            for record in stream.read():
                # print(f"adding record to queue {record}")
                if is_first_record:
                    is_first_record = False
                    self._message_repository.emit_message(
                        stream_status_as_airbyte_message(airbyte_stream.name, airbyte_stream.namespace, AirbyteStreamStatus.RUNNING)
                    )
                self._queue.put(record)
            self._message_repository.emit_message(
                stream_status_as_airbyte_message(airbyte_stream.name, airbyte_stream.namespace, AirbyteStreamStatus.COMPLETE)
            )
            self._queue.put(self._sentinel)
        except Exception as e:
            # print(f"exception: {e}")
            self._message_repository.emit_message(
                stream_status_as_airbyte_message(stream.name, stream.as_airbyte_stream().namespace, AirbyteStreamStatus.INCOMPLETE)
            )
            self._queue.put(e)
