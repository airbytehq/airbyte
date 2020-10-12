from airbyte_protocol import Source
from airbyte_protocol import AirbyteSpec
from airbyte_protocol import AirbyteCheckResponse
from airbyte_protocol import AirbyteSchema
from airbyte_protocol import AirbyteMessage
import urllib.request
from typing import Generator
from base_singer import SingerHelper


class SourceExchangeRatesApiSinger(Source):
    def __init__(self):
        pass

    def spec(self) -> AirbyteSpec:
        return SingerHelper.spec_from_file("/airbyte/exchangeratesapi-files/spec.json")

    def check(self, config_object, rendered_config_path) -> AirbyteCheckResponse:
        code = urllib.request.urlopen("https://api.exchangeratesapi.io/").getcode()
        return AirbyteCheckResponse(code == 200, {})

    def discover(self, config_object, rendered_config_path) -> AirbyteSchema:
        return SingerHelper.discover("tap-exchangeratesapi | grep '\"type\": \"SCHEMA\"' | head -1 | jq -c '{\"streams\":[{\"stream\": .stream, \"schema\": .schema}]}'")

    # todo: handle state
    def read(self, config_object, rendered_config_path, state=None) -> Generator[AirbyteMessage, None, None]:
        return SingerHelper.read(f"tap-exchangeratesapi --config {rendered_config_path}")
