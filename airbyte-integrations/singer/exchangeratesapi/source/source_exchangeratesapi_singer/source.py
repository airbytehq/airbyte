import urllib.request

from airbyte_protocol import AirbyteCheckResponse
from base_singer import SingerSource


class SourceExchangeRatesApiSinger(SingerSource):
    def __init__(self):
        pass

    def check(self, logger, config_path) -> AirbyteCheckResponse:
        code = urllib.request.urlopen("https://api.exchangeratesapi.io/").getcode()
        logger.info(f"Ping response code: {code}")
        return AirbyteCheckResponse(code == 200, {})

    def discover_cmd(self, logger, config_path) -> str:
        return "tap-exchangeratesapi | grep '\"type\": \"SCHEMA\"' | head -1 | jq -c '{\"streams\":[{\"stream\": .stream, \"schema\": .schema}]}'"

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        state_option = f"--state {state_path}" if state_path else ""
        return f"tap-exchangeratesapi --config {config_path} {state_option}"

