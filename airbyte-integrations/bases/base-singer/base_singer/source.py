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

from typing import Generator, Type

from airbyte_protocol import AirbyteCatalog, AirbyteMessage, ConfiguredAirbyteCatalog, AirbyteConnectionStatus, Status
from base_python import AirbyteLogger, CatalogHelper, ConfigContainer, Source

from .singer_helpers import SingerHelper


class SingerSource(Source):
    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        """
        Returns the command used to run discovery in the singer tap. For example, if the bash command used to invoke the singer tap is `tap-postgres`,
        and the config JSON lived in "/path/config.json", this method would return "tap-postgres --config /path/config.json"
        """
        raise NotImplementedError

    def read_cmd(self, logger: AirbyteLogger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        """
        Returns the command used to read data from the singer tap. For example, if the bash command used to invoke the singer tap is `tap-postgres`,
        and the config JSON lived in "/path/config.json", and the catalog was in "/path/catalog.json",
        this method would return "tap-postgres --config /path/config.json --catalog /path/catalog.json"
        """
        raise NotImplementedError

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
        masked_airbyte_catalog = ConfiguredAirbyteCatalog.parse_obj(self.read_config(catalog_path))
        selected_singer_catalog_path = SingerHelper.create_singer_catalog_with_selection(masked_airbyte_catalog, catalogs.singer_catalog)

        read_cmd = self.read_cmd(logger, config_container.rendered_config_path, selected_singer_catalog_path, state_path)
        return SingerHelper.read(logger, read_cmd)


class BaseSingerSource(SingerSource):
    force_full_refresh = False

    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        return f"{self.tap_cmd} --config {config_path} --discover"

    def read_cmd(self, logger: AirbyteLogger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        state_path = None if self.force_full_refresh else state_path
        args = {"--config": config_path, "--catalog": catalog_path, "--state": state_path}
        cmd = " ".join([f"{k} {v}" for k, v in args.items() if v is not None])

        return f"{self.tap_cmd} {cmd}"

    def check(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteConnectionStatus:
        try:
            json_config = config_container.rendered_config
            self.try_connect(logger, json_config)
        except self.api_error as err:
            logger.error("Exception while connecting to the %s: %s", self.tap_name, str(err))
            # this should be in UI
            error_msg = f"Unable to connect to the {self.tap_name} with the provided credentials. Error: {err}"
            return AirbyteConnectionStatus(status=Status.FAILED, message=error_msg)

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteCatalog:
        catalog = super().discover(logger, config_container)
        if self.force_full_refresh:
            return CatalogHelper.coerce_catalog_as_full_refresh(catalog)
        return catalog

    def try_connect(self, logger: AirbyteLogger, config: dict):
        """Test provided credentials, raises self.api_error if something goes wrong"""
        raise NotImplementedError

    @property
    def api_error(self) -> Type[Exception]:
        """Class/Base class of the exception that will be thrown if the tap is misconfigured or service unavailable"""
        raise NotImplementedError

    @property
    def tap_cmd(self) -> str:
        """Tap command"""
        raise NotImplementedError

    @property
    def tap_name(self) -> str:
        """Tap name"""
        raise NotImplementedError
