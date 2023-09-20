#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import concurrent
from concurrent.futures import Future
from functools import lru_cache
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.availability_strategy import AbstractAvailabilityStrategy
from airbyte_cdk.sources.streams.concurrent.concurrent_partition_generator import ConcurrentPartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.partitions.partition_generator import PartitionGenerator


class ThreadBasedConcurrentStream(AbstractStream):
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
    def name(self) -> str:
        """
        :return: Stream name. By default, this is the implementing class name, but it can be overridden as needed.
        """
        return self._name

    def __init__(
        self,
        partition_generator: PartitionGenerator,
        max_workers: int,
        name: str,
        json_schema: Mapping[str, Any],
        availability_strategy: AbstractAvailabilityStrategy,
        primary_key: Optional[Union[str, List[str], List[List[str]]]],
        cursor_field: Union[str, List[str]],
    ):
        self._stream_partition_generator = partition_generator
        self._max_workers = max_workers
        self._threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool")
        self._name = name
        self._json_schema = json_schema
        self._primary_key = primary_key
        self._cursor_field = cursor_field
        self._availability_strategy = availability_strategy

    def check_availability(self) -> Tuple[bool, Optional[str]]:
        if self._availability_strategy:
            return self._availability_strategy.check_availability(self.logger)
        else:
            return True, None
        raise NotImplementedError

    def read(self) -> Iterable[StreamData]:
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
            while partition_generator.has_partition_ready():
                partition = partition_generator.get_next()
                if partition is not None:
                    futures.append(self._threadpool.submit(partition_reader.process_partition, partition))
        self._check_for_errors(futures)

    def _is_done(self, futures: List[Future[Any]]) -> bool:
        return all(future.done() for future in futures)

    def _check_for_errors(self, futures: List[Future[Any]]) -> None:
        exceptions_from_futures = [f for f in [future.exception() for future in futures] if f is not None]
        if exceptions_from_futures:
            raise RuntimeError(f"Failed reading from stream {self.name} with errors: {exceptions_from_futures}")
