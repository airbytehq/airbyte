import urllib.request

from airbyte_protocol import AirbyteConnectionStatus
from base_singer import SingerSource


class SourceExchangeRatesApiSinger(SingerSource):
    def __init__(self):
        pass

    def check(self, logger, config_path) -> AirbyteConnectionStatus:
        try:
            code = urllib.request.urlopen("https://api.exchangeratesapi.io/").getcode()
            logger.info(f"Ping response code: {code}")
            return AirbyteConnectionStatus(status=(code == 200))
        except Exception as e:
            return AirbyteConnectionStatus(status=False, message=f"{str(e)}")


    def discover_cmd(self, logger, config_path) -> str:
        return "tap-exchangeratesapi | grep '\"type\": \"SCHEMA\"' | head -1 | jq -c '{\"streams\":[{\"stream\": .stream, \"schema\": .schema}]}'"

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        state_option = f"--state {state_path}" if state_path else ""
        return f"tap-exchangeratesapi --config {config_path} {state_option}"

