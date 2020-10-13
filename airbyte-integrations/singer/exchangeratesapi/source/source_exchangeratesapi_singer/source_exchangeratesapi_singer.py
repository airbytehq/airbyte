from airbyte_protocol import Source
from airbyte_protocol import AirbyteSpec
from airbyte_protocol import AirbyteCheckResponse
from airbyte_protocol import AirbyteCatalog
from airbyte_protocol import AirbyteMessage
import urllib.request
from typing import Generator
from base_singer import SingerHelper
from base_singer import Catalogs


def get_catalogs(logger) -> Catalogs:
    return SingerHelper.discover(logger, "tap-exchangeratesapi | grep '\"type\": \"SCHEMA\"' | head -1 | jq -c '{\"streams\":[{\"stream\": .stream, \"schema\": .schema}]}'")


class SourceExchangeRatesApiSinger(Source):
    def __init__(self):
        pass

    def spec(self) -> AirbyteSpec:
        return SingerHelper.spec_from_file("/airbyte/exchangeratesapi-files/spec.json")

    def check(self, logger, config_container) -> AirbyteCheckResponse:
        code = urllib.request.urlopen("https://api.exchangeratesapi.io/").getcode()
        return AirbyteCheckResponse(code == 200, {})

    def discover(self, logger, config_container) -> AirbyteCatalog:
        return get_catalogs(logger).airbyte_catalog

    def read(self, logger, config_container, catalog_path, state=None) -> Generator[AirbyteMessage, None, None]:
        if state:
            return SingerHelper.read(logger, f"tap-exchangeratesapi --config {config_container.rendered_config_path} --state {state}")
        else:
            return SingerHelper.read(logger, f"tap-exchangeratesapi --config {config_container.rendered_config_path}")
