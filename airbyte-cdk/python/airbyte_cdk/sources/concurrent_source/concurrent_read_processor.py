#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Dict, Iterable, List, Optional, Set

from airbyte_cdk.exception_handler import generate_failed_streams_error_message
from airbyte_cdk.models import AirbyteMessage, AirbyteStreamStatus, FailureType, StreamDescriptor
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.concurrent_source.stream_thread_exception import StreamThreadException
from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message


class ConcurrentReadProcessor:
    def __init__(
        self,
        stream_instances_to_read_from: List[AbstractStream],
        partition_enqueuer: PartitionEnqueuer,
        thread_pool_manager: ThreadPoolManager,
        logger: logging.Logger,
        slice_logger: SliceLogger,
        message_repository: MessageRepository,
        partition_reader: PartitionReader,
    ):
        """
        This class is responsible for handling items from a concurrent stream read process.
        :param stream_instances_to_read_from: List of streams to read from
        :param partition_enqueuer: PartitionEnqueuer instance
        :param thread_pool_manager: ThreadPoolManager instance
        :param logger: Logger instance
        :param slice_logger: SliceLogger instance
        :param message_repository: MessageRepository instance
        :param partition_reader: PartitionReader instance
        """
        self._stream_name_to_instance = {s.name: s for s in stream_instances_to_read_from}
        self._record_counter = {}
        self._streams_to_running_partitions: Dict[str, Set[Partition]] = {}
        for stream in stream_instances_to_read_from:
            self._streams_to_running_partitions[stream.name] = set()
            self._record_counter[stream.name] = 0
        self._thread_pool_manager = thread_pool_manager
        self._partition_enqueuer = partition_enqueuer
        self._stream_instances_to_start_partition_generation = stream_instances_to_read_from
        self._streams_currently_generating_partitions: List[str] = []
        self._logger = logger
        self._slice_logger = slice_logger
        self._message_repository = message_repository
        self._partition_reader = partition_reader
        self._streams_done: Set[str] = set()
        self._exceptions_per_stream_name: dict[str, List[Exception]] = {}

    def on_partition_generation_completed(self, sentinel: PartitionGenerationCompletedSentinel) -> Iterable[AirbyteMessage]:
        """
        This method is called when a partition generation is completed.
        1. Remove the stream from the list of streams currently generating partitions
        2. If the stream is done, mark it as such and return a stream status message
        3. If there are more streams to read from, start the next partition generator
        """
        stream_name = sentinel.stream.name
        self._streams_currently_generating_partitions.remove(sentinel.stream.name)
        # It is possible for the stream to already be done if no partitions were generated
        # If the partition generation process was completed and there are no partitions left to process, the stream is done
        if self._is_stream_done(stream_name) or len(self._streams_to_running_partitions[stream_name]) == 0:
            yield from self._on_stream_is_done(stream_name)
        if self._stream_instances_to_start_partition_generation:
            yield self.start_next_partition_generator()  # type:ignore # None may be yielded

    def on_partition(self, partition: Partition) -> None:
        """
        This method is called when a partition is generated.
        1. Add the partition to the set of partitions for the stream
        2. Log the slice if necessary
        3. Submit the partition to the thread pool manager
        """
        stream_name = partition.stream_name()
        self._streams_to_running_partitions[stream_name].add(partition)
        if self._slice_logger.should_log_slice_message(self._logger):
            self._message_repository.emit_message(self._slice_logger.create_slice_log_message(partition.to_slice()))
        self._thread_pool_manager.submit(self._partition_reader.process_partition, partition)

    def on_partition_complete_sentinel(self, sentinel: PartitionCompleteSentinel) -> Iterable[AirbyteMessage]:
        """
        This method is called when a partition is completed.
        1. Close the partition
        2. If the stream is done, mark it as such and return a stream status message
        3. Emit messages that were added to the message repository
        """
        partition = sentinel.partition

        try:
            if sentinel.is_successful:
                partition.close()
        except Exception as exception:
            self._flag_exception(partition.stream_name(), exception)
            yield AirbyteTracedException.from_exception(
                exception, stream_descriptor=StreamDescriptor(name=partition.stream_name())
            ).as_sanitized_airbyte_message()
        finally:
            partitions_running = self._streams_to_running_partitions[partition.stream_name()]
            if partition in partitions_running:
                partitions_running.remove(partition)
                # If all partitions were generated and this was the last one, the stream is done
                if partition.stream_name() not in self._streams_currently_generating_partitions and len(partitions_running) == 0:
                    yield from self._on_stream_is_done(partition.stream_name())
            yield from self._message_repository.consume_queue()

    def on_record(self, record: Record) -> Iterable[AirbyteMessage]:
        """
        This method is called when a record is read from a partition.
        1. Convert the record to an AirbyteMessage
        2. If this is the first record for the stream, mark the stream as RUNNING
        3. Increment the record counter for the stream
        4. Ensures the cursor knows the record has been successfully emitted
        5. Emit the message
        6. Emit messages that were added to the message repository
        """
        # Do not pass a transformer or a schema
        # AbstractStreams are expected to return data as they are expected.
        # Any transformation on the data should be done before reaching this point
        message = stream_data_to_airbyte_message(record.partition.stream_name(), record.data)
        stream = self._stream_name_to_instance[record.partition.stream_name()]

        if message.type == MessageType.RECORD:
            if self._record_counter[stream.name] == 0:
                self._logger.info(f"Marking stream {stream.name} as RUNNING")
                yield stream_status_as_airbyte_message(stream.as_airbyte_stream(), AirbyteStreamStatus.RUNNING)
            self._record_counter[stream.name] += 1
            stream.cursor.observe(record)
        yield message
        yield from self._message_repository.consume_queue()

    def on_exception(self, exception: StreamThreadException) -> Iterable[AirbyteMessage]:
        """
        This method is called when an exception is raised.
        1. Stop all running streams
        2. Raise the exception
        """
        self._flag_exception(exception.stream_name, exception.exception)
        self._logger.exception(f"Exception while syncing stream {exception.stream_name}", exc_info=exception.exception)

        stream_descriptor = StreamDescriptor(name=exception.stream_name)
        if isinstance(exception.exception, AirbyteTracedException):
            yield exception.exception.as_airbyte_message(stream_descriptor=stream_descriptor)
        else:
            yield AirbyteTracedException.from_exception(exception, stream_descriptor=stream_descriptor).as_airbyte_message()

    def _flag_exception(self, stream_name: str, exception: Exception) -> None:
        self._exceptions_per_stream_name.setdefault(stream_name, []).append(exception)

    def start_next_partition_generator(self) -> Optional[AirbyteMessage]:
        """
        Start the next partition generator.
        1. Pop the next stream to read from
        2. Submit the partition generator to the thread pool manager
        3. Add the stream to the list of streams currently generating partitions
        4. Return a stream status message
        """
        if self._stream_instances_to_start_partition_generation:
            stream = self._stream_instances_to_start_partition_generation.pop(0)
            self._thread_pool_manager.submit(self._partition_enqueuer.generate_partitions, stream)
            self._streams_currently_generating_partitions.append(stream.name)
            self._logger.info(f"Marking stream {stream.name} as STARTED")
            self._logger.info(f"Syncing stream: {stream.name} ")
            return stream_status_as_airbyte_message(
                stream.as_airbyte_stream(),
                AirbyteStreamStatus.STARTED,
            )
        else:
            return None

    def is_done(self) -> bool:
        """
        This method is called to check if the sync is done.
        The sync is done when:
        1. There are no more streams generating partitions
        2. There are no more streams to read from
        3. All partitions for all streams are closed
        """
        is_done = all([self._is_stream_done(stream_name) for stream_name in self._stream_name_to_instance.keys()])
        if is_done and self._exceptions_per_stream_name:
            error_message = generate_failed_streams_error_message(self._exceptions_per_stream_name)
            self._logger.info(error_message)
            # We still raise at least one exception when a stream raises an exception because the platform currently relies
            # on a non-zero exit code to determine if a sync attempt has failed. We also raise the exception as a config_error
            # type because this combined error isn't actionable, but rather the previously emitted individual errors.
            raise AirbyteTracedException(
                message=error_message, internal_message="Concurrent read failure", failure_type=FailureType.config_error
            )
        return is_done

    def _is_stream_done(self, stream_name: str) -> bool:
        return stream_name in self._streams_done

    def _on_stream_is_done(self, stream_name: str) -> Iterable[AirbyteMessage]:
        self._logger.info(f"Read {self._record_counter[stream_name]} records from {stream_name} stream")
        self._logger.info(f"Marking stream {stream_name} as STOPPED")
        stream = self._stream_name_to_instance[stream_name]
        stream.cursor.ensure_at_least_one_state_emitted()
        yield from self._message_repository.consume_queue()
        self._logger.info(f"Finished syncing {stream.name}")
        self._streams_done.add(stream_name)
        stream_status = (
            AirbyteStreamStatus.INCOMPLETE if self._exceptions_per_stream_name.get(stream_name, []) else AirbyteStreamStatus.COMPLETE
        )
        yield stream_status_as_airbyte_message(stream.as_airbyte_stream(), stream_status)
