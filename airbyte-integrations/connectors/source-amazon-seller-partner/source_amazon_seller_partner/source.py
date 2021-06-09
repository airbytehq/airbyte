#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import json
from typing import Any, Generator, Mapping, MutableMapping

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Status,
    SyncMode,
)
from airbyte_cdk.sources import Source

from .client import BaseClient


class SourceAmazonSellerPartner(Source):

    client_class = BaseClient

    def _get_client(self, config: Mapping):
        client = self.client_class(**config)
        return client

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        client = self._get_client(config)
        logger.info("Checking access to Amazon SP-API")
        try:
            client.check_connection()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        client = self._get_client(config)

        return AirbyteCatalog(streams=client.get_streams())

    def read(
        self, logger: AirbyteLogger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: MutableMapping[str, Any] = None
    ) -> Generator[AirbyteMessage, None, None]:
        client = self._get_client(config)

        logger.info("Starting syncing Amazon Seller API")
        for configured_stream in catalog.streams:
            yield from self._read_record(logger=logger, client=client, configured_stream=configured_stream, state=state)

        logger.info("Finished syncing Amazon Seller API")

    @staticmethod
    def _read_record(
        logger: AirbyteLogger, client: BaseClient, configured_stream: ConfiguredAirbyteStream, state: MutableMapping[str, Any]
    ) -> Generator[AirbyteMessage, None, None]:
        stream_name = configured_stream.stream.name
        is_report = client._amazon_client.is_report(stream_name)

        if configured_stream.sync_mode == SyncMode.full_refresh:
            state.pop(stream_name, None)

        if is_report:
            yield from client.read_reports(logger, stream_name, state)
        else:
            yield from client.read_stream(logger, stream_name, state)
