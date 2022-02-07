#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, MutableMapping

from airbyte_cdk.sources.deprecated.base_source import BaseClient, BaseSource, ConfiguredAirbyteStream

from .client import Client


class SourceHubspot(BaseSource):
    client_class = Client

    def _read_stream(
        self, logger: logging.Logger, client: BaseClient, configured_stream: ConfiguredAirbyteStream, state: MutableMapping[str, Any]
    ):
        """
        This method is overridden to check if the stream exists in the client.
        """
        stream_name = configured_stream.stream.name
        if not client._apis.get(stream_name):
            logger.warning(f"Stream {stream_name} does not exist in the client.")
            return
        yield from super()._read_stream(logger=logger, client=client, configured_stream=configured_stream, state=state)
