from airbyte_protocol import Source
from airbyte_protocol import AirbyteSpec
from airbyte_protocol import AirbyteCheckResponse
from airbyte_protocol import AirbyteCatalog
from airbyte_protocol import AirbyteMessage
import urllib.request
from typing import Generator
from base_singer import SingerHelper
from base_singer import Catalogs


def get_catalogs() -> Catalogs:
    return SingerHelper.discover("tap-exchangeratesapi | grep '\"type\": \"SCHEMA\"' | head -1 | jq -c '{\"streams\":[{\"stream\": .stream, \"schema\": .schema}]}'")


class SourceExchangeRatesApiSinger(Source):
    def __init__(self):
        pass

    def spec(self) -> AirbyteSpec:
        return SingerHelper.spec_from_file("/airbyte/exchangeratesapi-files/spec.json")

    def check(self, config_object, rendered_config_path) -> AirbyteCheckResponse:
        code = urllib.request.urlopen("https://api.exchangeratesapi.io/").getcode()
        return AirbyteCheckResponse(code == 200, {})

    def discover(self, config_object, rendered_config_path) -> AirbyteCatalog:
        return get_catalogs().airbyte_catalog

    def read(self, config_object, rendered_config_path, catalog_path, state=None) -> Generator[AirbyteMessage, None, None]:
        airbyte_catalog = catalog_path # todo: read

        # call discover
        singer_catalog = get_catalogs().singer_catalog

        # todo: combine discovered singer catalog with the generated airbyte catalog

        sync_prefix = f"tap-exchangeratesapi --config {rendered_config_path}"
        if state:
            return SingerHelper.read(sync_prefix + f"--state {state}")
        else:
            return SingerHelper.read(sync_prefix)
