"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from datetime import datetime
from typing import Dict, Generator, Mapping, Type

from airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    Status,
)
from airbyte_protocol import Type as MessageType

from .client import BaseClient
from .integration import Source
from .logger import AirbyteLogger


class BaseSource(Source):
    """Base source that designed to work with clients derived from BaseClient"""

    client_class: Type[BaseClient] = None

    def _get_client(self, config: Mapping):
        """Construct client"""
        client = self.client_class(**config)

        return client

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        """Discover streams"""
        client = self._get_client(config)

        return AirbyteCatalog(streams=[stream for stream in client.streams])

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """Check connection"""
        client = self._get_client(config)
        alive, error = client.health_check()
        if not alive:
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(error))

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any] = {}
    ) -> Generator[AirbyteMessage, None, None]:
        client = self._get_client(config)

        logger.info(f"Starting syncing {self.__class__.__name__}")
        total_state = {**state}
        for configured_stream in catalog.streams:
            stream_name = configured_stream.stream.name

            if client.stream_has_state(stream_name) and state.get(stream_name):
                logger.info(f"Set state of {stream_name} stream to {state.get(stream_name)}")
                client.set_stream_state(stream_name, state.get(stream_name))

            logger.info(f"Syncing {stream_name} stream")
            for record in client.read_stream(configured_stream.stream):
                now = int(datetime.now().timestamp()) * 1000
                message = AirbyteRecordMessage(stream=stream_name, data=record, emitted_at=now)
                yield AirbyteMessage(type=MessageType.RECORD, record=message)

            if client.stream_has_state(stream_name):
                total_state[stream_name] = client.get_stream_state(stream_name)
                # output state object only together with other stream states
                yield AirbyteMessage(type=MessageType.STATE, state=AirbyteStateMessage(data=total_state))

        logger.info(f"Finished syncing {self.__class__.__name__}")
