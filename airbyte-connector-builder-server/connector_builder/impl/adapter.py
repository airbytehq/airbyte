#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List

from airbyte_cdk.models import AirbyteMessage
from airbyte_cdk.sources.streams.http import HttpStream


class CdkAdapter(ABC):
    """
    Abstract base class for the connector builder's CDK adapter.
    """

    @abstractmethod
    def get_http_streams(self, config: Dict[str, Any]) -> List[HttpStream]:
        """
        Gets a list of HTTP streams.

        :param config: The user-provided configuration as specified by the source's spec.
        :return: A list of `HttpStream`s.
        """

    @abstractmethod
    def read_stream(self, stream: str, config: Dict[str, Any]) -> Iterator[AirbyteMessage]:
        """
        Reads data from the specified stream.

        :param stream: stream
        :param config: The user-provided configuration as specified by the source's spec.
        :return: An iterator over `AirbyteMessage` objects.
        """


class CdkAdapterFactory(ABC):

    @abstractmethod
    def create(self, manifest: Dict[str, Any]) -> CdkAdapter:
        """Return an implementation of CdkAdapter"""
        pass
