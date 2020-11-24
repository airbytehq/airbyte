""" MIT License

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

from typing import Type, Generator

from airbyte_protocol import (
    AirbyteCatalog, AirbyteConnectionStatus, AirbyteMessage,
    ConfiguredAirbyteCatalog, Status
)

from .logger import AirbyteLogger
from .client import BaseClient
from .integration import ConfigContainer, Source


class BaseSource(Source):
    """ Base source that designed to work with clients derived from BaseClient
    """
    client_class: Type[BaseClient] = None

    def _get_client(self, config_container: ConfigContainer):
        """ Construct client
        """
        config = config_container.rendered_config
        client = self.client_class(**config)

        return client

    def discover(self, logger: AirbyteLogger,
                 config_container: ConfigContainer) -> AirbyteCatalog:
        """
        """
        client = self._get_client(config_container)

        return AirbyteCatalog(streams=client.streams)

    def check(self, logger: AirbyteLogger,
              config_container: ConfigContainer) -> AirbyteConnectionStatus:
        """
        """
        client = self._get_client(config_container)
        alive, error = client.health_check()
        if not alive:
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message=str(error)
            )

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def read(
            self, logger: AirbyteLogger, config_container: ConfigContainer,
            catalog_path, state=None
    ) -> Generator[AirbyteMessage, None, None]:
        client = self._get_client(config_container)

        config = self.read_config(catalog_path)
        catalog = ConfiguredAirbyteCatalog.parse_obj(config)

        logger.info(f"Starting syncing {self.__class__.__name__}")
        for configured_stream in catalog.streams:
            yield from client.read_stream(configured_stream.stream)
        logger.info(f"Finished syncing {self.__class__.__name__}")
