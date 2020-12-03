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

from airbyte_protocol import AirbyteConnectionStatus
from base_python import AirbyteLogger, ConfigContainer
from base_singer import SingerSource
from tap_intercom.client import IntercomClient, IntercomError


class BaseSingerSource(SingerSource):
    tap_cmd = None

    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        return f"{self.tap_cmd} --config {config_path} --discover"

    def read_cmd(self, logger: AirbyteLogger, config_path: str,
                 catalog_path: str, state_path: str = None) -> str:
        args = {
            "--config": config_path,
            "--catalog": catalog_path,
            "--state": state_path
        }
        cmd = " ".join([f"{k} {v}" for k, v in args.items() if v is not None])

        return f"{self.tap_cmd} {cmd}"

    def check(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteConnectionStatus:
        try:
            json_config = config_container.rendered_config
            self.try_connect(logger, json_config)
        except IntercomError as err:
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


class SourceIntercomSinger(BaseSingerSource):
    tap_cmd = "tap-intercom"
    tap_name = "Intercom API"

    def try_connect(self, logger: AirbyteLogger, config: dict):
        client = IntercomClient(user_agent=config["user_agent"], api_key=config["api_key"])
        ok = client.check_access_token()
        if not ok:
            raise IntercomError(f"Got an empty response from {self.tap_name}, check your permissions")
