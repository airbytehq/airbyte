from abc import abstractmethod, ABC
from collections.abc import AsyncIterable
from dataclasses import dataclass, field
from typing import Mapping, Any, Iterable, TypeVar, Union, Generic

from airbyte_cdk.v2.concurrency import PartitionDescriptor, PartitionGenerator

from airbyte_cdk.sources.connector_state_manager import HashableStreamDescriptor

from airbyte_cdk.sources.streams.core import StreamData
from airbyte_protocol.models import ConfiguredAirbyteCatalog

from airbyte_cdk.v2 import Stream, State
from airbyte_cdk.v2.state import StateManager

# from airbyte_cdk.v2.state import StateManager

PartitionType = TypeVar('PartitionType', bound='PartitionDescriptor')
StateType = TypeVar('StateType', bound=State)


class PartitionedStream(Stream, ABC, Generic[PartitionType]):
    """
    TL;DR this class is most useful for incremental syncs and high performance syncs e.g via concurrency.

    A partitioned stream is a stream whose partitions (the contiguous non-overlapping subsets of records) can be retrieved independently.
    This stream contains utilities for state management
    """
    state_manager: StateManager
    # concurrency_policy: Optional[ConcurrencyPolicy] TODO probably?

    def __init__(self, state_manager: StateManager[StateType, PartitionType]):
        self.state_manager = state_manager

    @abstractmethod
    def get_partition_descriptors(self, stream_state: StateType, catalog: ConfiguredAirbyteCatalog) -> Iterable[PartitionType]:
        """ Return the partition descriptors """

    @abstractmethod
    async def parse_response(self, response: Any) -> AsyncIterable[StreamData]:
        """
        TODO this feels like a weird place to put this. A stream has no obligation to outside objects to provide
            a method for parsing output, it feels like an intrusion on this abstraction. Either this is not a stream
            (e.g when using with a ConcurrentStreamGroup it's a StreamInfoProvider or something) and it makes sense
            to provide this method, or it's a stream and it doesn't make sense to expose such a low level implementation
            detail. But this method and read_partition/read_stream don't really coexist I think.
        @param response:
        @return:
        """

    # Is the stream making each request, or is it essentially asking the source to make the request, and the source
    # makes the request on its behalf? This allows the source to coordinate requests to minimize rate limit issues
    # etc.
    # I think it's better that the stream can make its own request, and that concurrency share a client object as needed
    # Otherwise it's a bit hard to have concurrency which make different request patterns e.g sync & async, or REST and GQL
    # in the same connector. Although maybe this just means that the concurrency should each be grouped under a "request queue" which
    # achieves maximum parallelism even across concurrency.
    # Should this return only records? What about log/trace/state messages, or records from a different stream?
    # re: log/trace yes it should be able to return that probably
    # re:
    @abstractmethod
    async def read_partition(self, configured_catalog: ConfiguredAirbyteCatalog, partition: PartitionType):
        """"""

    def read_stream(self, config, catalog, state) -> Iterable[StreamData]:
        # TODO read the partitions according to the stream's concurrency policy
        # for part in self.get_partition_descriptors(state, catalog):
        #     for record_or_message in await self.read_partition(catalog, part):
        #         yield record_or_message
        #         if isinstance(record_or_message, dict):
        #             self.state_manager.observe(record_or_message)
        #     self.state_manager.notify_partition_complete(part)

        pass

# HTTP
