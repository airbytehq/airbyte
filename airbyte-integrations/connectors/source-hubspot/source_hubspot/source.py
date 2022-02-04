#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, MutableMapping

from airbyte_cdk.sources.deprecated.base_source import BaseSource, BaseClient
from airbyte_cdk.models import ConfiguredAirbyteStream

from .client import Client


class SourceHubspot(BaseSource):
    client_class = Client

    def _read_stream(
        self, logger: logging.Logger, client: BaseClient, configured_stream: ConfiguredAirbyteStream, state: MutableMapping[str, Any]
    ):
        stream_name = configured_stream.stream.name
        if not client._apis.get(stream_name):
            logger.warning(f"Stream {stream_name} is not in the source.")
            return
        yield from super()._read_stream(logger=logger, client=client, configured_stream=configured_stream, state=state)
