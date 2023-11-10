#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent
import logging
from abc import ABC
from concurrent.futures import Future
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from typing import Any, Callable, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Set, Union

from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, AirbyteStreamStatus, ConfiguredAirbyteCatalog
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel, QueueItem
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.sources.utils.schema_helpers import split_config
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message


class Status(Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"


@dataclass
class PartitionReadStatus:
    partition: Partition
    partition_read_status: Status


@dataclass
class StreamReadStatus:
    stream: AbstractStream
    partition_generation_status: Status
    partition_read_statuses: List[PartitionReadStatus]


class ConcurrentSource(AbstractSource, ABC):
    def __init__(
        self, max_workers: int, timeout_in_seconds: int, message_repository: MessageRepository = InMemoryMessageRepository(), **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self._max_workers = max_workers
        self._timeout_seconds = timeout_in_seconds
        self._threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool")
        self._message_repository = message_repository

    @property
    def message_repository(self) -> MessageRepository:
        return self._message_repository

    # FIXME: This probably deserves a nicer interface with an adapter
    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[Union[List[AirbyteStateMessage], MutableMapping[str, Any]]] = None,
    ) -> Iterator[AirbyteMessage]:
        logger.info(f"Starting syncing {self.name}")
        futures: List[Future[Any]] = []
        queue: Queue[QueueItem] = Queue()
        partition_enqueuer = PartitionEnqueuer(queue)
        config, internal_config = split_config(config)
        stream_to_instance_map: Mapping[str, AbstractStream] = {s.name: s for s in self._streams_as_abstract_streams(config)}
        max_number_of_partition_generator_in_progress = max(1, self._max_workers // 2)

        stream_instances_to_read_from = self._get_streams_to_read_from(catalog, logger, stream_to_instance_map)
        streams_currently_generating_partitions: List[str] = []
        streams_to_partitions: Dict[str, Set[Partition]] = {}
        record_counter = {}
        for stream in stream_instances_to_read_from:
            streams_to_partitions[stream.name] = set()
            record_counter[stream.name] = 0
        if not stream_instances_to_read_from:
            return
        while len(streams_currently_generating_partitions) < max_number_of_partition_generator_in_progress:
            yield self._start_next_partition_generator(
                stream_instances_to_read_from,
                futures,
                streams_currently_generating_partitions,
                partition_enqueuer,
                logger,
            )
        yield from self._consume_from_queue(
            queue,
            logger,
            streams_to_partitions,
            partition_enqueuer,
            streams_currently_generating_partitions,
            stream_instances_to_read_from,
            futures,
            record_counter,
            stream_to_instance_map,
        )
        # TODO Some sort of error handling
        self._check_for_errors(futures)
        self._threadpool.shutdown(wait=False, cancel_futures=True)
        logger.info(f"Finished syncing {self.name}")

    def _consume_from_queue(
        self,
        queue: Queue[QueueItem],
        logger: logging.Logger,
        streams_to_partitions: Dict[str, Set[Partition]],
        partition_enqueuer: PartitionEnqueuer,
        streams_currently_generating_partitions: List[str],
        stream_instances_to_read_from: List[AbstractStream],
        futures: List[Future[Any]],
        record_counter: Dict[str, int],
        stream_to_instance_map: Mapping[str, AbstractStream],
    ) -> Iterable[AirbyteMessage]:
        partition_reader = PartitionReader(queue)
        while airbyte_message_or_record_or_exception := queue.get(block=True, timeout=self._timeout_seconds):
            yield from self._handle_item(
                airbyte_message_or_record_or_exception,
                streams_to_partitions,
                logger,
                streams_currently_generating_partitions,
                stream_instances_to_read_from,
                partition_enqueuer,
                futures,
                record_counter,
                partition_reader,
                stream_to_instance_map,
            )
            if self._is_done(streams_to_partitions, stream_instances_to_read_from, streams_currently_generating_partitions):
                # all partitions were generated and process. we're done here
                if all([f.done() for f in futures]) and queue.empty():
                    break

    def _handle_item(
        self,
        queue_item: QueueItem,
        streams_to_partitions: Dict[str, Set[Partition]],
        logger: logging.Logger,
        streams_currently_generating_partitions: List[str],
        stream_instances_to_read_from: List[AbstractStream],
        partition_enqueuer: PartitionEnqueuer,
        futures: List[Future[Any]],
        record_counter: Dict[str, int],
        partition_reader: PartitionReader,
        stream_to_instance_map: Mapping[str, AbstractStream],
    ) -> Iterable[AirbyteMessage]:
        if isinstance(queue_item, Exception):
            # An exception was raised while processing the stream
            # Stop the threadpool and raise it
            yield from self._stop_streams(streams_to_partitions, logger, stream_to_instance_map)
            raise queue_item

        elif isinstance(queue_item, PartitionGenerationCompletedSentinel):
            yield from self._handle_partition_generation_completed(
                queue_item,
                streams_currently_generating_partitions,
                stream_instances_to_read_from,
                partition_enqueuer,
                futures,
                logger,
                streams_to_partitions,
                record_counter,
                stream_to_instance_map,
            )

        elif isinstance(queue_item, Partition):
            # a new partition was generated and must be processed
            self._handle_partition(queue_item, streams_to_partitions, futures, partition_reader, logger)
        elif isinstance(queue_item, PartitionCompleteSentinel):
            # all records for a partition were generated
            partition = queue_item.partition
            status_message = self._handle_partition_completed(
                partition, streams_to_partitions, record_counter, streams_currently_generating_partitions, logger, stream_to_instance_map
            )
            yield from self._message_repository.consume_queue()
            if status_message:
                yield status_message
        else:
            # record
            yield from self._handle_record(queue_item, record_counter, logger, stream_to_instance_map)

    def _get_streams_to_read_from(
        self, catalog: ConfiguredAirbyteCatalog, logger: logging.Logger, stream_to_instance_map: Mapping[str, AbstractStream]
    ) -> List[AbstractStream]:
        stream_instances_to_read_from = []
        for configured_stream in catalog.streams:
            stream_instance = stream_to_instance_map.get(configured_stream.stream.name)
            if not stream_instance:
                if not self.raise_exception_on_missing_stream:
                    continue
                raise KeyError(
                    f"The stream {configured_stream.stream.name} no longer exists in the configuration. "
                    f"Refresh the schema in replication settings and remove this stream from future sync attempts."
                )
            else:
                stream_availability = stream_instance.check_availability()
                if not stream_availability.is_available():
                    logger.warning(
                        f"Skipped syncing stream '{stream_instance.name}' because it was unavailable. {stream_availability.message()}"
                    )
                    continue
                stream_instances_to_read_from.append(stream_instance)
        return stream_instances_to_read_from

    def _is_done(
        self,
        streams_to_partitions: Dict[str, Set[Partition]],
        stream_instances_to_read_from: List[AbstractStream],
        streams_currently_generating_partitions: List[str],
    ) -> bool:
        return (
            not streams_currently_generating_partitions
            and not stream_instances_to_read_from
            and all([all(p.is_closed() for p in partitions) for partitions in streams_to_partitions.values()])
        )

    def _check_for_errors(self, futures: List[Future[Any]]) -> None:
        exceptions_from_futures = [f for f in [future.exception() for future in futures] if f is not None]
        if exceptions_from_futures:
            exception = RuntimeError(f"Failed reading from stream {self.name} with errors: {exceptions_from_futures}")
            self._stop_and_raise_exception(exception)
        else:
            futures_not_done = [f for f in futures if not f.done()]
            if futures_not_done:
                exception = RuntimeError(f"Failed reading from stream {self.name} with futures not done: {futures_not_done}")
                self._stop_and_raise_exception(exception)

    def _stop_and_raise_exception(self, exception: BaseException) -> None:
        self._threadpool.shutdown(wait=False, cancel_futures=True)
        raise exception

    def _start_next_partition_generator(
        self,
        streams: List[AbstractStream],
        futures: List[Future[Any]],
        streams_currently_generating_partitions: List[str],
        partition_enqueuer: PartitionEnqueuer,
        logger: logging.Logger,
    ) -> AirbyteMessage:
        stream = streams.pop(0)
        self._submit_task(futures, partition_enqueuer.generate_partitions, stream)
        streams_currently_generating_partitions.append(stream.name)
        logger.info(f"Marking stream {stream.name} as STARTED")
        logger.info(f"Syncing stream: {stream.name} ")
        return stream_status_as_airbyte_message(
            # FIXME pass namespace
            stream.name,
            None,
            AirbyteStreamStatus.STARTED,
        )

    def _handle_record(
        self, record: Record, record_counter: Dict[str, int], logger: logging.Logger, stream_to_instance_map: Mapping[str, AbstractStream]
    ) -> Iterable[AirbyteMessage]:
        # Do not pass a transformer or a schema
        # AbstractStreams are expected to return data as they are expected.
        # Any transformation on the data should be done before reaching this point
        message = stream_data_to_airbyte_message(record.stream_name, record.data)
        stream = stream_to_instance_map[record.stream_name]
        status_message = None
        if record_counter[stream.name] == 0:
            logger.info(f"Marking stream {stream.name} as RUNNING")

            status_message = stream_status_as_airbyte_message(
                stream.name, stream.as_airbyte_stream().namespace, AirbyteStreamStatus.RUNNING
            )
        if message.type == MessageType.RECORD:
            record_counter[stream.name] += 1
        if status_message:
            return [status_message, message] + list(self._message_repository.consume_queue())
        else:
            return [message] + list(self._message_repository.consume_queue())

    def _handle_partition(
        self,
        partition: Partition,
        streams_to_partitions: Mapping[str, Set[Partition]],
        futures: List[Future[Any]],
        partition_reader: PartitionReader,
        logger: logging.Logger,
    ) -> None:
        stream_name = partition.stream_name()
        streams_to_partitions[stream_name].add(partition)
        if self._slice_logger.should_log_slice_message(logger):
            self._message_repository.emit_message(self._slice_logger.create_slice_log_message(partition.to_slice()))
        self._submit_task(futures, partition_reader.process_partition, partition)

    def _handle_partition_generation_completed(
        self,
        sentinel: PartitionGenerationCompletedSentinel,
        streams_currently_generating_partitions: List[str],
        stream_instances_to_read_from: List[AbstractStream],
        partition_enqueuer: PartitionEnqueuer,
        futures: List[Future[Any]],
        logger: logging.Logger,
        streams_to_partitions: Dict[str, Set[Partition]],
        record_counter: Dict[str, int],
        stream_to_instance_map: Mapping[str, AbstractStream],
    ) -> List[AirbyteMessage]:
        stream_name = sentinel.stream.name
        streams_currently_generating_partitions.remove(sentinel.stream.name)
        ret = []
        if self._is_stream_done(stream_name, streams_to_partitions, streams_currently_generating_partitions):
            ret.append(self._handle_stream_is_done(stream_name, record_counter, logger, stream_to_instance_map))
        if stream_instances_to_read_from:
            ret.append(
                self._start_next_partition_generator(
                    stream_instances_to_read_from, futures, streams_currently_generating_partitions, partition_enqueuer, logger
                )
            )
        return ret

    def _handle_partition_completed(
        self,
        partition: Partition,
        streams_to_partitions: Dict[str, Set[Partition]],
        record_counter: Dict[str, int],
        streams_currently_generating_partitions: List[str],
        logger: logging.Logger,
        stream_to_instance_map: Mapping[str, AbstractStream],
    ) -> Optional[AirbyteMessage]:
        stream_name = partition.stream_name()
        partition.close()
        if self._is_stream_done(stream_name, streams_to_partitions, streams_currently_generating_partitions):
            return self._handle_stream_is_done(stream_name, record_counter, logger, stream_to_instance_map)
        else:
            return None

    def _is_stream_done(
        self, stream_name: str, streams_to_partitions: Dict[str, Set[Partition]], streams_currently_generating_partitions: List[str]
    ) -> bool:
        return (
            all([p.is_closed() for p in streams_to_partitions[stream_name]]) and stream_name not in streams_currently_generating_partitions
        )

    def _handle_stream_is_done(
        self, stream_name: str, record_counter: Dict[str, int], logger: logging.Logger, stream_to_instance_map: Mapping[str, AbstractStream]
    ) -> AirbyteMessage:
        logger.info(f"Read {record_counter[stream_name]} records from {stream_name} stream")
        logger.info(f"Marking stream {stream_name} as STOPPED")
        stream = stream_to_instance_map[stream_name]
        logger.info(f"Finished syncing {stream.name}")
        return stream_status_as_airbyte_message(stream.name, stream.as_airbyte_stream().namespace, AirbyteStreamStatus.COMPLETE)

    def _stop_streams(
        self, stream_to_partitions: Dict[str, Set[Partition]], logger: logging.Logger, stream_to_instance_map: Mapping[str, AbstractStream]
    ) -> Iterable[AirbyteMessage]:
        self._threadpool.shutdown(wait=False, cancel_futures=True)
        for stream_name, partitions in stream_to_partitions.items():
            stream = stream_to_instance_map[stream_name]
            if not all([p.is_closed() for p in partitions]):
                logger.info(f"Marking stream {stream.name} as STOPPED")
                logger.info(f"Finished syncing {stream.name}")
                yield stream_status_as_airbyte_message(stream.name, stream.as_airbyte_stream().namespace, AirbyteStreamStatus.INCOMPLETE)

    def _submit_task(self, futures: List[Future[Any]], function: Callable[..., Any], *args: Any) -> None:
        # Submit a task to the threadpool, waiting if there are too many pending tasks
        # self._wait_while_too_many_pending_futures(futures)
        futures.append(self._threadpool.submit(function, *args))

    def _streams_as_abstract_streams(self, config: Mapping[str, Any]) -> List[AbstractStream]:
        streams = self.streams(config)
        streams_as_abstract_streams = []
        for stream in streams:
            if isinstance(stream, StreamFacade):
                streams_as_abstract_streams.append(stream._abstract_stream)
            else:
                raise ValueError(f"Only StreamFacade is supported by ConcurrentSource. Got {stream}")
        return streams_as_abstract_streams
