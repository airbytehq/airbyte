#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import concurrent
import logging
from concurrent.futures import Future
from functools import lru_cache
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.source import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.concurrent.concurrent_partition_generator import ConcurrentPartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.partitions.legacy import LegacyPartitionGenerator
from airbyte_cdk.sources.streams.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_cdk.sources.utils.types import StreamData


class AvailabilityStrategyLegacyAdapter(AvailabilityStrategy):
    """
    This class is used to adapt the legacy Stream's Availability so it can be used from a ConcurrentStream.
    """

    def __init__(self, stream: Stream, availability_strategy: AvailabilityStrategy):
        self._stream = stream
        self._availability_strategy = availability_strategy

    def check_availability(self, stream: AbstractStream, logger: logging.Logger, source: Optional[Source]) -> Tuple[bool, Optional[str]]:
        if stream.name != self._stream.name:
            raise ValueError(
                f"AvailabilityStrategyLegacyAdapter can only be used with the stream it was initialized with. Expected {self._stream.name}, got {stream.name}"
            )

        return self._availability_strategy.check_availability(self._stream, logger, source)


class ConcurrentStream(AbstractStream):
    @classmethod
    def create_from_legacy_stream(cls, stream: Stream, max_workers: int) -> "ConcurrentStream":
        """
        Create a ConcurrentStream from a legacy Stream.
        :param stream:
        :param max_workers:
        :return:
        """
        return ConcurrentStream(
            partition_generator=LegacyPartitionGenerator(stream),
            max_workers=max_workers,
            name=stream.name,
            json_schema=stream.get_json_schema(),
            availability_strategy=AvailabilityStrategyLegacyAdapter(stream, stream.availability_strategy)
            if stream.availability_strategy
            else None,
            primary_key=stream.primary_key,
            cursor_field=stream.cursor_field,
        )

    def __init__(
        self,
        partition_generator: PartitionGenerator,
        max_workers: int,
        name: str,
        json_schema: Mapping[str, Any],
        availability_strategy: Optional[AvailabilityStrategy],
        primary_key: Optional[Union[str, List[str], List[List[str]]]],
        cursor_field: Union[str, List[str]],
    ):
        self._stream_partition_generator = partition_generator
        self._max_workers = max_workers
        self._threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool")
        self._name = name
        self._json_schema = json_schema
        self._availability_strategy = availability_strategy
        self._primary_key = primary_key
        self._cursor_field = cursor_field

    def read(
        self,
        cursor_field: Optional[List[str]],
        logger: logging.Logger,
        slice_logger: SliceLogger,
        internal_config: InternalConfig = InternalConfig(),
    ) -> Iterable[StreamData]:
        logger.debug(f"Processing stream slices for {self.name} (sync_mode: full_refresh)")
        total_records_counter = 0
        futures = []
        partition_generator = ConcurrentPartitionGenerator()
        partition_reader = PartitionReader()

        # Submit partition generation tasks
        futures.append(
            self._threadpool.submit(partition_generator.generate_partitions, self._stream_partition_generator, SyncMode.full_refresh)
        )

        # Run as long as there are partitions to process or records to read
        while not (partition_generator.is_done() and partition_reader.is_done() and self._is_done(futures)):
            self._check_for_errors(futures)

            # While there is a partition to process
            while partition_reader.has_record_ready():
                record = partition_reader.get_next()
                if record is not None:
                    yield record.stream_data
                    if AbstractStream.is_record(record.stream_data):
                        total_records_counter += 1
                        if internal_config and internal_config.is_limit_reached(total_records_counter):
                            return
            while partition_generator.has_partition_ready():
                partition = partition_generator.get_next()
                if partition is not None:
                    futures.append(self._threadpool.submit(partition_reader.process_partition, partition))
                    if slice_logger.should_log_slice_message(logger):
                        # FIXME: This is creating slice log messages for parity with the synchronous implementation
                        # but these cannot be used by the connector builder to build slices because they can be unordered
                        yield slice_logger.create_slice_log_message(partition.to_slice())
        self._check_for_errors(futures)

    def _is_done(self, futures: List[Future[Any]]) -> bool:
        return all(future.done() for future in futures)

    def _check_for_errors(self, futures: List[Future[Any]]) -> None:
        exceptions_from_futures = [f for f in [future.exception() for future in futures] if f is not None]
        if exceptions_from_futures:
            raise RuntimeError(f"Failed reading from stream {self.name} with errors: {exceptions_from_futures}")

    @property
    def name(self) -> str:
        return self._name

    def check_availability(self, logger: logging.Logger, source: Optional["Source"] = None) -> Tuple[bool, Optional[str]]:
        if self._availability_strategy:
            return self._availability_strategy.check_availability(self, logger, source)
        else:
            return True, None

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return self._cursor_field

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        return self._json_schema

    @property
    def source_defined_cursor(self) -> bool:
        return True
