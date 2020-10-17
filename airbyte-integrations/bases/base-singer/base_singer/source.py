from airbyte_protocol import AirbyteCatalog
from airbyte_protocol import AirbyteMessage
from airbyte_protocol import Source
from typing import Generator

from .singer_helpers import SingerHelper


class SingerSource(Source):

    def discover_cmd(self, logger, config_path) -> str:
        raise Exception("Not Implemented")

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        raise Exception("Not Implemented")

    def discover(self, logger, config_container) -> AirbyteCatalog:
        cmd = self.discover_cmd(logger, config_container.rendered_config_path)
        catalogs = SingerHelper.get_catalogs(logger, cmd)

        return catalogs.airbyte_catalog

    def read(self, logger, config_container, catalog_path, state_path=None) -> Generator[AirbyteMessage, None, None]:
        discover_cmd = self.discover_cmd(logger, config_container.rendered_config_path)
        catalogs = SingerHelper.get_catalogs(logger, discover_cmd)
        masked_airbyte_catalog = self.read_config(catalog_path)
        selected_singer_catalog_path = SingerHelper.create_singer_catalog_with_selection(masked_airbyte_catalog, catalogs.singer_catalog)

        read_cmd = self.read_cmd(logger, config_container.rendered_config_path, selected_singer_catalog_path, state_path)
        return SingerHelper.read(logger, read_cmd)
