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

from typing import Generator

from airbyte_protocol import AirbyteCatalog, AirbyteMessage
from base_python import AirbyteLogger, ConfigContainer, Source

from .singer_helpers import SingerHelper


class SingerSource(Source):
    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        """
        Returns the command used to run discovery in the singer tap. For example, if the bash command used to invoke the singer tap is `tap-postgres`,
        and the config JSON lived in "/path/config.json", this method would return "tap-postgres --config /path/config.json"
        """
        raise Exception("Not Implemented")

    def read_cmd(self, logger: AirbyteLogger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        """
        Returns the command used to read data from the singer tap. For example, if the bash command used to invoke the singer tap is `tap-postgres`,
        and the config JSON lived in "/path/config.json", and the catalog was in "/path/catalog.json",
        this method would return "tap-postgres --config /path/config.json --catalog /path/catalog.json"
        """
        raise Exception("Not Implemented")

    def discover(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteCatalog:
        """
        Implements the parent class discover method.
        """
        cmd = self.discover_cmd(logger, config_container.rendered_config_path)
        catalogs = SingerHelper.get_catalogs(logger, cmd)

        return catalogs.airbyte_catalog

    def read(
        self, logger: AirbyteLogger, config_container: ConfigContainer, catalog_path: str, state_path: str = None
    ) -> Generator[AirbyteMessage, None, None]:
        """
        Implements the parent class read method.
        """
        discover_cmd = self.discover_cmd(logger, config_container.rendered_config_path)
        catalogs = SingerHelper.get_catalogs(logger, discover_cmd)
        masked_airbyte_catalog = self.read_config(catalog_path)
        selected_singer_catalog_path = SingerHelper.create_singer_catalog_with_selection(masked_airbyte_catalog, catalogs.singer_catalog)

        read_cmd = self.read_cmd(logger, config_container.rendered_config_path, selected_singer_catalog_path, state_path)
        return SingerHelper.read(logger, read_cmd)
