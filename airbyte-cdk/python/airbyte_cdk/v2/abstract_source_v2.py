from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Mapping, Any, TypeVar, Iterable, Optional, Union, List, Tuple

from airbyte_cdk.sources import Source

from airbyte_cdk.sources.streams.core import StreamData
from airbyte_protocol.models import ConfiguredAirbyteCatalog, AirbyteCatalog, AirbyteConnectionStatus, Status

from airbyte_cdk.v2 import Stream


class AbstractSource(Source, ABC):
    """
    Abstract base class for an Airbyte Source. Consumers should implement any abstract methods
    in this class to create an Airbyte Specification compliant Source.
    """

    SLICE_LOG_PREFIX = "slice:"
    # Stream name to instance map for applying output object transformation
    _stream_to_instance_map: Mapping[str, Stream] = {}

    @abstractmethod
    def check_connection(self, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        :param config: The user-provided configuration as specified by the source's spec.
          This usually contains information required to check connection e.g. tokens, secrets and keys etc.
        :return: A tuple of (boolean, error). If boolean is true, then the connection check is successful
          and we can connect to the underlying data source using the provided configuration.
          Otherwise, the input config cannot be used to connect to the underlying data source,
          and the "error" object should describe what went wrong.
          The error object will be cast to string to display the problem to the user.
        """

    @abstractmethod
    def streams(self, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog = None) -> Iterable[Stream]:
        """
        :param config: The user-provided configuration as specified by the source's spec.
        Any stream construction related operation should happen here.
        :return: A list of the concurrency in this source connector.
        """

    @property
    def name(self) -> str:
        """Source name"""
        return self.__class__.__name__

    def discover(self, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Implements the Discover operation from the Airbyte Specification.
        See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#discover.
        """
        streams = [stream.as_airbyte_stream() for stream in self.streams(config=config)]
        return AirbyteCatalog(streams=streams)

    def check(self, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Implements the Check Connection operation from the Airbyte Specification.
        See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#check.
        """
        check_succeeded, error = self.check_connection(config)
        if not check_succeeded:
            return AirbyteConnectionStatus(status=Status.FAILED, message=repr(error))
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

# HTTP

