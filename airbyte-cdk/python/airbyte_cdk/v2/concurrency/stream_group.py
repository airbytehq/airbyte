from abc import ABC, abstractmethod
from typing import List, Mapping, Any, Generic, TypeVar

from airbyte_protocol.models import ConfiguredAirbyteCatalog, AirbyteMessage

from airbyte_cdk.v2 import Stream
from airbyte_cdk.v2.concurrency import  PartitionedStream, PartitionDescriptor

PartitionType = TypeVar('PartitionType', bound=PartitionDescriptor)
class AsyncRetriever(ABC, Generic[PartitionType]):
    concurrency_policy: ConcurrencyPolicy

    async def retrieve(self, ):


class PartitionedStreamGroup(ABC):
    retriever: AsyncRetriever
    _streams: List[PartitionedStream]

    def streams(self, configured_catalog: ConfiguredAirbyteCatalog) -> List[Stream]:
        return self._streams

    def read_all(self, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: Mapping[str, Any]) -> AirbyteMessage:

