"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from airbyte_protocol import AirbyteConnectionStatus, Status
from base_python import AirbyteLogger, ConfigContainer
from base_singer import SingerSource
from tap_mixpanel.client import MixpanelClient, MixpanelError


class BaseSingerSource(SingerSource):
    tap_cmd = None
    tap_name = None
    api_error = Exception

    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        return f"{self.tap_cmd} --config {config_path} --discover"

    def read_cmd(self, logger: AirbyteLogger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        args = {"--config": config_path, "--catalog": catalog_path, "--state": state_path}
        cmd = " ".join([f"{k} {v}" for k, v in args.items() if v is not None])

        return f"{self.tap_cmd} {cmd}"

    def check(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteConnectionStatus:
        try:
            json_config = config_container.rendered_config
            self.try_connect(logger, json_config)
        except self.api_error as err:
            logger.error("Exception while connecting to the %s: %s", self.tap_name, str(err))
            # this should be in UI
            error_msg = (
                f"Unable to connect to the {self.tap_name} with the provided credentials. "
                "Please make sure the input credentials and environment are correct. "
                f"Error: {err}"
            )
            return AirbyteConnectionStatus(status=Status.FAILED, message=error_msg)

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def try_connect(self, logger: AirbyteLogger, config: dict):
        raise NotImplementedError


class SourceMixpanelSinger(BaseSingerSource):
    tap_cmd = "tap-mixpanel"
    tap_name = "Mixpanel API"
    api_error = MixpanelClient
    client_class = MixpanelError

    def transform_config(self, raw_config):
        airbyte_config = {
            "user_agent": "tap-mixpanel contact@airbyte.io",
            "api_secret": raw_config["api_key"],
            "start_date": raw_config.get("start_date"),
            "date_window_size": raw_config.get("date_window_size", 30),
            "attribution_window": raw_config.get("attribution_window", 5),
            "project_timezone": raw_config.get("US/Pacific"),
            "select_properties_by_default": raw_config.get("select_properties_by_default"),
        }
        # drop None values as some of them has no default fallback
        return {k: v for k, v in airbyte_config.items() if v is not None}

    def try_connect(self, logger: AirbyteLogger, config: dict):
        client = self.client_class(user_agent=config["user_agent"], api_secret=config["api_secret"])
        ok = client.check_access_token()
        if not ok:
            raise self.api_error(f"Got an empty response from {self.tap_name}, check your permissions")
