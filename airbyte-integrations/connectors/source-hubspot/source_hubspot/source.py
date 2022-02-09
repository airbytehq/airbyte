#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Mapping, Any, Tuple, Optional, List

from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import AirbyteCatalog
from airbyte_cdk.sources.deprecated.base_source import BaseSource
from airbyte_cdk.sources import AbstractSource

from .client import Client


# class SourceHubspot(BaseSource):
#     client_class = Client


class SourceHubspot(AbstractSource):
    client_class = Client

    def _get_client(self, config: Mapping):
        """Construct client"""
        return self.client_class(**config)

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """Check connection"""
        client = self._get_client(config)
        alive, error = client.health_check()
        if not alive:
            return False, error
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        client = self._get_client(config)
        return client.stream_instances()

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:  # TODO refactor use
        """List of available streams, patch streams to append properties dynamically"""
        streams = []
        for stream_instance in self.streams(config=config):
            stream = stream_instance.as_airbyte_stream()
            properties = stream_instance.properties
            if properties:
                stream.json_schema["properties"]["properties"] = {"type": "object", "properties": properties}
                stream.default_cursor_field = [stream_instance.updated_at_field]
            streams.append(stream)

        return AirbyteCatalog(streams=streams)
