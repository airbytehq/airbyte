import requests
from airbyte_protocol import AirbyteCatalog
from airbyte_protocol import AirbyteCheckResponse
from airbyte_protocol import AirbyteMessage
from airbyte_protocol import Source
from base_singer import SingerHelper
from typing import Generator


class SourceStripeSinger(Source):
    def __init__(self):
        pass

    def check(self, logger, config_container) -> AirbyteCheckResponse:
        json_config = config_container.rendered_config
        r = requests.get('https://api.stripe.com/v1/customers', auth=(json_config['client_secret'], ''))

        return AirbyteCheckResponse(r.status_code == 200, {})

    def discover(self, logger, config_container) -> AirbyteCatalog:
        catalogs = SingerHelper.get_catalogs(logger, f"tap-stripe --config {config_container.rendered_config_path} --discover")
        return catalogs.airbyte_catalog

    def read(self, logger, config_container, catalog_path, state=None) -> Generator[AirbyteMessage, None, None]:
        discover_cmd = f"tap-stripe --config {config_container.rendered_config_path} --discover"
        discovered_singer_catalog = SingerHelper.get_catalogs(logger, discover_cmd).singer_catalog

        masked_airbyte_catalog = self.read_config(catalog_path)
        selected_singer_catalog = SingerHelper.create_singer_catalog_with_selection(masked_airbyte_catalog, discovered_singer_catalog)

        config_option = f"--config {config_container.rendered_config_path}"
        catalog_option = f"--catalog {selected_singer_catalog}"
        state_option = f"--state {state}" if state else ""
        return SingerHelper.read(logger, f"tap-stripe {config_option} {catalog_option} {state_option}")
