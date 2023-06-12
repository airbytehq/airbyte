import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Mapping, Any, Generic, TypeVar, Iterable, AsyncIterable

from airbyte_cdk.sources.connector_state_manager import HashableStreamDescriptor
from airbyte_protocol.models import ConfiguredAirbyteCatalog, AirbyteMessage, Type as MessageType

from airbyte_cdk.v2.concurrency import PartitionedStream, PartitionDescriptor, ConcurrencyPolicy
from airbyte_cdk.v2.state import State

PartitionType = TypeVar('PartitionType', bound=PartitionDescriptor)
ResponseType = TypeVar('ResponseType')
StateType = TypeVar('StateType', bound=State)


@dataclass
class StreamAndPartition(Generic[PartitionType]):
    stream: PartitionedStream
    partition_descriptor: PartitionType


class AsyncRequester(ABC, Generic[PartitionType]):
    @abstractmethod
    # TODO this likely needs to be an async iterable
    async def request(self, partition_descriptor: PartitionType) -> ResponseType:
        """ Retrieves the data associated with the input partition descriptor"""
        # TODO this should be able to handle differing pagination/error handling/etc.. strategies between partitions


class PartitionedStreamGroup(ABC, Generic[PartitionType]):
    requester: AsyncRequester
    concurrency_policy: ConcurrencyPolicy
    _streams: List[PartitionedStream]

    def streams(self, configured_catalog: ConfiguredAirbyteCatalog) -> List[PartitionedStream]:
        # TODO
        return self._streams

    async def _read_partition(self, partition_and_stream: StreamAndPartition[PartitionType]) -> AsyncIterable[AirbyteMessage]:
        partition_descriptor = partition_and_stream.partition_descriptor
        stream_state_manager = partition_and_stream.stream.state_manager
        # TODO parsing and error handling
        # TODO this likely needs to be an async for because request() should probably return an async iterable
        for record_or_message in await self.requester.request(partition_descriptor):
            yield record_or_message
            if isinstance(record_or_message, dict):
                if state_message := stream_state_manager.observe(record_or_message):
                    yield state_message
            if isinstance(record_or_message, AirbyteMessage) and record_or_message.type == MessageType.RECORD:
                if state_message := stream_state_manager.observe(record_or_message.record.data):
                    yield state_message

        yield stream_state_manager.notify_partition_complete(partition_descriptor)

    async def _read_partitions_async(self, partitions_with_streams: Iterable[StreamAndPartition[PartitionType]]):
        semaphore = asyncio.Semaphore(self.concurrency_policy.maximum_number_of_concurrent_requests())
        for partition_and_stream in partitions_with_streams:
            # Acquire the semaphore so we can schedule as many concurrent requests as the concurrencypolicy allows
            async with semaphore:
                async for x in self._read_partition(partition_and_stream):
                    # You can't do "yield from" on an async iterable :(
                    yield x

    def read_all(self,
                 config: Mapping[str, Any],
                 catalog: ConfiguredAirbyteCatalog,
                 source_state: Mapping[HashableStreamDescriptor, State]
                 ) -> Iterable[AirbyteMessage]:
        partition_descriptors = self.get_partition_descriptors(catalog=catalog, source_state=source_state)

        # This is probably too naive/static of a way to specify concurrency. We might need something better that
        # dynamically reacts to server responses. Two examples of where this might be useful:
        #   - if the responses from the server for some reason require us to reduce our number of concurrent workers
        #   - if the server says backoff for 30 seconds, it's likely that all requests should back off for that time period
        yield from asyncio.run(self._read_partitions_async(partition_descriptors))

    def get_partition_descriptors(self,
                                  catalog: ConfiguredAirbyteCatalog,
                                  source_state: Mapping[HashableStreamDescriptor, State]
                                  ) -> Iterable[StreamAndPartition[PartitionType]]:
        # TODO allow getting the last partition from each stream's partitions so we can enable fast first-syncs
        # TODO allow round-robin getting one stream from each partition to enable "balanced" syncs
        for stream in self._streams:
            stream_state = source_state[stream.get_stream_descriptor()]
            for partition in stream.get_partition_descriptors(stream_state=stream_state, catalog=catalog):
                yield StreamAndPartition(stream=stream, partition_descriptor=partition)
