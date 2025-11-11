# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import Any, Iterable, Mapping, Optional, cast

from airbyte_cdk.sources.declarative.retrievers import Retriever
from airbyte_cdk.sources.declarative.schema import SchemaLoader
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer_test_read_decorator import (
    StreamSlicerTestReadDecorator,
)
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.stream_slicer import StreamSlicer
from airbyte_cdk.sources.types import Record, StreamSlice
from airbyte_cdk.utils.slice_hasher import SliceHasher


# For Connector Builder test read operations, we track the total number of records
# read for the stream so that we can stop reading early if we exceed the record limit.
class RecordCounter:
    def __init__(self) -> None:
        self.total_record_counter = 0

    def increment(self) -> None:
        self.total_record_counter += 1

    def reset(self) -> None:
        self.total_record_counter = 0

    def get_total_records(self) -> int:
        return self.total_record_counter


class DeclarativePartitionFactory:
    def __init__(
        self,
        stream_name: str,
        schema_loader: SchemaLoader,
        retriever: Retriever,
        message_repository: MessageRepository,
        max_records_limit: Optional[int] = None,
    ) -> None:
        """
        The DeclarativePartitionFactory takes a retriever_factory and not a retriever directly. The reason is that our components are not
        thread safe and classes like `DefaultPaginator` may not work because multiple threads can access and modify a shared field across each other.
        In order to avoid these problems, we will create one retriever per thread which should make the processing thread-safe.
        """
        self._stream_name = stream_name
        self._schema_loader = schema_loader
        self._retriever = retriever
        self._message_repository = message_repository
        self._max_records_limit = max_records_limit
        self._record_counter = RecordCounter()

    def create(self, stream_slice: StreamSlice) -> Partition:
        return DeclarativePartition(
            stream_name=self._stream_name,
            schema_loader=self._schema_loader,
            retriever=self._retriever,
            message_repository=self._message_repository,
            max_records_limit=self._max_records_limit,
            stream_slice=stream_slice,
            record_counter=self._record_counter,
        )


class DeclarativePartition(Partition):
    def __init__(
        self,
        stream_name: str,
        schema_loader: SchemaLoader,
        retriever: Retriever,
        message_repository: MessageRepository,
        max_records_limit: Optional[int],
        stream_slice: StreamSlice,
        record_counter: RecordCounter,
    ):
        self._stream_name = stream_name
        self._schema_loader = schema_loader
        self._retriever = retriever
        self._message_repository = message_repository
        self._max_records_limit = max_records_limit
        self._stream_slice = stream_slice
        self._hash = SliceHasher.hash(self._stream_name, self._stream_slice)
        self._record_counter = record_counter

    def read(self) -> Iterable[Record]:
        if self._max_records_limit is not None:
            if self._record_counter.get_total_records() >= self._max_records_limit:
                return
        for stream_data in self._retriever.read_records(
            self._schema_loader.get_json_schema(), self._stream_slice
        ):
            if self._max_records_limit is not None:
                if self._record_counter.get_total_records() >= self._max_records_limit:
                    break

            if isinstance(stream_data, Mapping):
                record = (
                    stream_data
                    if isinstance(stream_data, Record)
                    else Record(
                        data=stream_data,
                        stream_name=self.stream_name(),
                        associated_slice=self._stream_slice,
                    )
                )
                yield record
            else:
                self._message_repository.emit_message(stream_data)

            if self._max_records_limit is not None:
                self._record_counter.increment()

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return self._stream_slice

    def stream_name(self) -> str:
        return self._stream_name

    def __hash__(self) -> int:
        return self._hash


class StreamSlicerPartitionGenerator(PartitionGenerator):
    def __init__(
        self,
        partition_factory: DeclarativePartitionFactory,
        stream_slicer: StreamSlicer,
        slice_limit: Optional[int] = None,
        max_records_limit: Optional[int] = None,
    ) -> None:
        self._partition_factory = partition_factory

        if slice_limit:
            self._stream_slicer = cast(
                StreamSlicer,
                StreamSlicerTestReadDecorator(
                    wrapped_slicer=stream_slicer,
                    maximum_number_of_slices=slice_limit,
                ),
            )
        else:
            self._stream_slicer = stream_slicer

    def generate(self) -> Iterable[Partition]:
        for stream_slice in self._stream_slicer.stream_slices():
            yield self._partition_factory.create(stream_slice)
