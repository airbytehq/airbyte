from abc import abstractmethod, ABC
from functools import lru_cache
from typing import Mapping, Any, List

from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader

from airbyte_cdk.sources.streams.core import StreamData, package_name_from_class
from airbyte_protocol.models import ConfiguredAirbyteCatalog

from airbyte_cdk.v2.state import StateType


class Stream(ABC):
    # TODO we might want to have a concept of a partitioned stream be separate from a stream in case that makes the UX easier for
    #  non-partitioned concurrency
    namespace: str
    name: str
    primary_key: List[List[str]]

    # @abstractmethod
    def read_stream(self, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: StateType) -> StreamData:
        """
        :raises
            FatalException
            RescheduleSyncException
        """
        pass

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.

        The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        Override as needed.
        """
        # TODO show an example of using pydantic to define the JSON schema, or reading an OpenAPI spec
        # TODO usage package_name_from_class might be wrong here since it might
        return ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema(self.name)


print(package_name_from_class(Stream.__class__))

