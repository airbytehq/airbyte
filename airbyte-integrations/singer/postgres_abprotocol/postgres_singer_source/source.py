import urllib.request
import psycopg2

from typing import Generator

from airbyte_protocol import AirbyteCatalog
from airbyte_protocol import AirbyteConnectionStatus
from airbyte_protocol import Status
from airbyte_protocol import AirbyteMessage
from airbyte_protocol import Source
from airbyte_protocol import ConfigContainer
from base_singer import SingerHelper, SingerSource


TAP_CMD = "PGCLIENTENCODING=UTF8 tap-postgres"
class PostgresSingerSource(SingerSource):
    def __init__(self):
        pass

    def check(self, logger, config_container: ConfigContainer) -> AirbyteConnectionStatus:
        config = config_container.rendered_config
        try:
            params="dbname='{dbname}' user='{user}' host='{host}' password='{password}' port='{port}'".format(**config)
            psycopg2.connect(params)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            logger.error(f"Exception while connecting to postgres database: {e}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))

    def discover_cmd(self, logger, config_container: ConfigContainer) -> AirbyteCatalog:
        return f"{TAP_CMD} --config {config_container.rendered_config_path} --discover"

    def read_cmd(self, logger, config_container: ConfigContainer, catalog_option: str, state=None) -> Generator[AirbyteMessage, None, None]:
        catalog_path = f"--properties {selected_singer_catalog}"
        config_option = f"--config {config_container.rendered_config_path}"
        state_option = f"--state {state}" if state else ""
        return f"{TAP_CMD} {catalog_path} {config_option} {state_option}"
