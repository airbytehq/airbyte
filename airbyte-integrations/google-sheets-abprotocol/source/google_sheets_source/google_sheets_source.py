from airbyte_protocol import Source
from airbyte_protocol import AirbyteSpec
from airbyte_protocol import AirbyteCheckResponse
from airbyte_protocol import AirbyteCatalog
from airbyte_protocol import AirbyteMessage
import requests
from typing import Generator
from base_singer import SingerHelper

WORKSPACE_ROOT = "/airbyte/google_sheets_source"

class GoogleSheetsSource(Source):
    def __init__(self):
        pass

    def spec(self) -> AirbyteSpec:
        return SingerHelper.spec_from_file(f"{WORKSPACE_ROOT}/spec.json")

    def check(self, logger, config_container) -> AirbyteCheckResponse:
        raise Exception("Not Implemented")

    def discover(self, logger, config_container) -> AirbyteCatalog:
        raise Exception("Not Implemented")

    def read(self, logger, config_container, catalog_path, state=None) -> Generator[AirbyteMessage, None, None]:
        # masked_airbyte_catalog = self.read_config(catalog_path)
        # discovered_singer_catalog = SingerHelper.get_catalogs(logger, f"tap-stripe --config {config_container.rendered_config_path} --discover").singer_catalog
        # selected_singer_catalog = SingerHelper.create_singer_catalog_with_selection(masked_airbyte_catalog, discovered_singer_catalog)
        #
        # config_option = f"--config {config_container.rendered_config_path}"
        # catalog_option = f"--catalog {selected_singer_catalog}"
        # state_option = f"--state {state}" if state else ""
        raise Exception("Not Implemented")
        # return SingerHelper.read(logger, f"tap-stripe {config_option} {catalog_option} {state_option}")
