#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.models import AirbyteStreamStatus
from airbyte_cdk.sources.concurrent_source.stream_complete_sentinel import StreamCompleteSentinel
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message


class StreamReader:
    # FIXME: a lot of the code can probably be shared with the PartitionEnqueuer and PartitionReader
    def __init__(self, queue, sentinel, message_repository: MessageRepository, logger) -> None:
        self._queue = queue
        self._sentinel = sentinel
        self._message_repository = message_repository
        self._logger = logger

    def read_from_stream(self, stream: AbstractStream) -> None:
        # print(f"reading from stream: {stream.name}")
        try:
            airbyte_stream = stream.as_airbyte_stream()
            self._message_repository.emit_message(
                stream_status_as_airbyte_message(airbyte_stream.name, airbyte_stream.namespace, AirbyteStreamStatus.STARTED)
            )
            record_counter = 0
            for record in stream.read():
                if record_counter == 0:
                    self._message_repository.emit_message(
                        stream_status_as_airbyte_message(airbyte_stream.name, airbyte_stream.namespace, AirbyteStreamStatus.RUNNING)
                    )
                record_counter += 1
                self._queue.put(record)
            self._queue.put(StreamCompleteSentinel(stream))
            self._logger.info(f"Read {record_counter} records from {stream.name} stream")
        except Exception as e:
            self._queue.put(e)
