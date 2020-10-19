import requests
from airbyte_protocol import AirbyteConnectionStatus, Status
from base_singer import SingerSource


class SourceStripeSinger(SingerSource):
    def __init__(self):
        pass

    def check(self, logger, config_container) -> AirbyteCheckResponse:
        try:
            json_config = config_container.rendered_config
            r = requests.get('https://api.stripe.com/v1/customers', auth=(json_config['client_secret'], ''))
            if r.status_code == 200:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                return AirbyteConnectionStatus(status=Status.FAILED, message=r.text)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{str(e)}")

    def discover_cmd(self, logger, config_path) -> str:
        return f"tap-stripe --config {config_path} --discover"

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        config_option = f"--config {config_path}"
        catalog_option = f"--catalog {catalog_path}"
        state_option = f"--state {state_path}" if state_path else ""
        return f"tap-stripe {config_option} {catalog_option} {state_option}"
