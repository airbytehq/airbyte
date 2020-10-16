import requests
from airbyte_protocol import AirbyteCheckResponse
from base_singer import SingerSource


class SourceStripeSinger(SingerSource):
    def __init__(self):
        pass

    def check(self, logger, config_container) -> AirbyteCheckResponse:
        json_config = config_container.rendered_config
        r = requests.get('https://api.stripe.com/v1/customers', auth=(json_config['client_secret'], ''))

        return AirbyteCheckResponse(r.status_code == 200, {})

    def discover_cmd(self, logger, config_path) -> str:
        return f"tap-stripe --config {config_path} --discover"

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        config_option = f"--config {config_path}"
        catalog_option = f"--catalog {catalog_path}"
        state_option = f"--state {state_path}" if state_path else ""
        return f"tap-stripe {config_option} {catalog_option} {state_option}"
