from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from typing import Mapping, Any, Iterable, TypeVar, Union, Generic, Optional

from airbyte_cdk.sources.connector_state_manager import HashableStreamDescriptor

from airbyte_cdk.sources.streams.core import StreamData
from airbyte_protocol.models import ConfiguredAirbyteCatalog

from airbyte_cdk.v2.state import StateType, StateManager
from airbyte_cdk.v2.concurrency import Stream, ConcurrencyPolicy

PartitionType = TypeVar('PartitionType', bound='PartitionDescriptor')


@dataclass
class PartitionDescriptor:
    """
        TODO: A partition could be described by more than one thing e.g: date range and a configuration setting, for example:
            sync_deleted_records(bool) or lookback_window
            those are two examples of configurations which, if changed, the existing stream state is no longer correct, and the stream
            needs to be recomputed.
            Should we try to solve this as part of partition descriptors?

            Alternatively we could just not bother with this.
    """
    partition_id: str
    metadata: Mapping[str, Any]


class PartitionGenerator(ABC, Generic[PartitionType]):
    @abstractmethod
    def generate_partitions(self, state: StateType, catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any]) -> Iterable[
            PartitionType]:
        """ Generates partitions """


class PartitionedStream(Stream, ABC, Generic[PartitionType]):
    """
    TL;DR this class is most useful for incremental syncs and high performance syncs e.g via concurrency.

    A partitioned stream is a stream whose partitions (the contiguous non-overlapping subsets of records) can be retrieved independently.
    This stream contains utilities for state management
    """
    state_manager: StateManager
    concurrency_policy: Optional[ConcurrencyPolicy]

    @abstractmethod
    def get_partition_descriptors(self, stream_state: StateType, catalog: ConfiguredAirbyteCatalog) -> Iterable[PartitionType]:
        """ Return the partition descriptors """

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
class ErrorHandler:
    pass


class Paginator:
    pass


class ResponseParser:
    pass


@dataclass
class HttpRequestDescriptor:
    base_url: str
    path: str
    method: str
    headers: Mapping[str, Any] = field(default_factory=dict)
    cookies: Mapping[str, Any] = field(default_factory=dict)
    follow_redirects: bool = True


@dataclass
class GetRequest(HttpRequestDescriptor):
    request_parameters: Mapping[str, Any] = field(default_factory=dict)
    method: str = field(default="GET", init=False)


@dataclass
class PostRequest(HttpRequestDescriptor):
    body_data: Union[str, Mapping[str, Any]] = None
    body_json: Mapping[str, Any] = None
    method: str = field(default="POST", init=False)

    def __post_init__(self):
        num_input_body_params = sum(x is not None for x in [self.body_json, self.body_data])
        if num_input_body_params != 1:
            raise ValueError("Exactly one of of body_text, body_json, or body_urlencoded_params must be set")


@dataclass
class HttpPartitionDescriptor(PartitionDescriptor):
    request_descriptor: HttpRequestDescriptor


class SimpleHttpClient(ABC):
    # TODO
    pagination_policy: Paginator
    error_handling_policy: ErrorHandler

    def __init__(self):
        pass

    @abstractmethod
    async def request_async(self, descriptor: HttpRequestDescriptor):
        """"""

    @abstractmethod
    def request(self, descriptor: HttpRequestDescriptor):
        """"""


class HttpStream(Stream, ABC):
    def __init__(self, partition_generator: PartitionGenerator):
        pass
