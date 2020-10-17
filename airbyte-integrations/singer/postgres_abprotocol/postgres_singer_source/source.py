import urllib.request
import psycopg2

from typing import Generator

from airbyte_protocol import AirbyteCatalog
from airbyte_protocol import AirbyteCheckResponse
from airbyte_protocol import AirbyteMessage
from airbyte_protocol import Source
from airbyte_protocol import ConfigContainer
from base_singer import SingerHelper

TAP_CMD = "PGCLIENTENCODING=UTF8 tap-postgres"
class PostgresSingerSource(Source):
    def __init__(self):
        pass

    def check(self, logger, config_container: ConfigContainer) -> AirbyteCheckResponse:
        config = config_container.rendered_config
        try:
            psycopg2.connect(
                "dbname='{postgres_database}' user='{postgres_username}' host='{postgres_host}' password='{postgres_password}' port='{postgres_port}'".format(
                    **config))
            return AirbyteCheckResponse(True, {})
        except Exception as e:
            logger.error(f"Exception while connecting to postgres database: {e}")
            return AirbyteCheckResponse(False, {"reason": str(e)})

    def discover(self, logger, config_container) -> AirbyteCatalog:
        catalogs = SingerHelper.get_catalogs(logger, f"{TAP_CMD} --config {config_container.rendered_config_path} --discover")
        return catalogs.airbyte_catalog

    def read(self, logger, config_container, catalog_path, state=None) -> Generator[AirbyteMessage, None, None]:
        discover_cmd = f"{TAP_CMD} --config {config_container.rendered_config_path} --discover"
        discovered_singer_catalog = SingerHelper.get_catalogs(logger, discover_cmd).singer_catalog

        masked_airbyte_catalog = self.read_config(catalog_path)
        selected_singer_catalog = SingerHelper.create_singer_catalog_with_selection(masked_airbyte_catalog, discovered_singer_catalog)

        catalog_path = f"--properties {selected_singer_catalog}"
        config_option = f"--config {config_container.rendered_config_path}"
        state_option = f"--state {state}" if state else ""
        return SingerHelper.read(logger, f"{TAP_CMD} {catalog_path} {config_option} {state_option}")
